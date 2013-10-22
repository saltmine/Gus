import logging
import os.path
import tarfile
import re

from multiprocessing.dummy import Pool, Lock
import subprocess

from gus.models import chef_role
from gus.models import project
from gus.models import release_candidate

MAX_NUM_WORKERS = 4

log = logging.getLogger('gus.lib.deploy')


def run_as_subprocess(*args):
  """Wrap calling subprocess, and print the command before running it
  """
  print "Running: %s" % ' '.join(args)
  subprocess.check_call(args)


def _push_and_untar(box, tarball_source, target_dir, temp_dir='/tmp/'):
  """Push a tarball onto a remote machine and untar it
  """
  # TODO: Better temp dir
  target = "%s:%s" % (box, temp_dir)
  tarball_basename = os.path.basename(tarball_source)
  run_as_subprocess('/usr/bin/scp', tarball_source, target)
  run_as_subprocess('/usr/bin/ssh', box, 'tar', '-xzf',
      '/tmp/%s' % tarball_basename,
      '-C', target_dir)
  # TODO: delete or archive tarball?


def get_toplevel_dir_from_tarball(tarball_path):
  """If the tarball has a single top level directory, return its name.
  Otherwise, return None
  """
  if not os.path.isfile(tarball_path):
    return None
  tf = tarfile.open(tarball_path)
  top_level = tf.getmembers()
  if top_level[0].isdir():
    return top_level[0]
  else:
    return None


class Deploy(object):
  """Manage data and actions relevant to deploying code
  """

  def __init__(self, release_candidate_id, chef_api=None,
      deploy_user='outland'):
    self.chef_api = chef_api
    self.chef_app_prefs = None
    self.deploy_user = deploy_user  # TODO: get this from the project model

    # turn app:app_rev into tarball url
    self.rc = release_candidate.get_by_id(release_candidate_id)
    self.project = project.get_by_id(self.rc['project_id'])
    self.lock = Lock()
    self.nodes = []
    self.code_dir = None
    self.venv_dir = None

  @property
  def available_roles(self):
    """Get the list of available roles for this application. Roles are optional
    and the lack of them should return an empty list in which case every node
    can be deployed to. Throws if the app config hasn't been loaded from chef.
    """
    return chef_role.mget_by_project(self.project['project_id'])

  def deploy(self, env=None, roles=None, run_pre_activate_scripts=False):
    """Perform a deploy.
    """
    # does this app_rev exist for this app?
    #TODO: should we raise here?
    self.code_dir = get_toplevel_dir_from_tarball(
        self.rc['code_tarball_location'])
    self.venv_dir = get_toplevel_dir_from_tarball(
        self.rc['venv_tarball_location'])
    if not self.code_dir or not self.venv_dir:
      return None

    #dn = chef.Node('dev-monitor-001', api=self.chef_api)

    # Are the roles valid?
    target_role_names = set([r['chef_role_name'] for r in roles])
    available_role_names = set([r['chef_role_name']
      for r in self.available_roles])
    if (target_role_names | available_role_names) != available_role_names:
      raise RuntimeError("Attempting to deploy to invalid role: %s" % (
        target_role_names - available_role_names))

    self.load_node_list(roles, env)
    # can we deploy app to these nodes?
    if not self.nodes:
      return None

    # TODO: Upload static assets
    #if 'www' in roles:
      #self.upload_static_assets_to_cdn()

    # transfer tarballs to servers
    self._transfer()

    # Run pre-activate hook script on role migration
    # TODO: Make sure the script exists
    migration_tag = 'gus_migration'
    chef_query = "chef_environment:%s AND tags:%s" % (env['environment_name'],
        migration_tag)
    migration_node = self.chef_api.Search('node', chef_query)
    box = "%s@%s" % (self.deploy_user,
        migration_node['automatic']['ipaddress_eth1'])
    script = os.path.join([self.code_dir, self.project['pre_activate_hook']])
    run_as_subprocess('/usr/bin/ssh', box, '"%s"' % script, self.venv_dir)

    # activate on all machines
    self._activate()

    # TODO: Notify Hipchat

    # TODO: Ping statsd, if applicable

    # TODO: kick off smoke tests, if applicable

  def _transfer(self):
    '''Use a pool of workers to push the tarball out to the specified nodes
    '''
    pool = Pool(min(len(self.nodes, MAX_NUM_WORKERS)))
    res = pool.map(self._transfer_to_node, self.nodes)
    return res

  def _transfer_to_node(self, node):
    # Logging doesn't play nicely with multi-processing, so lock before
    # logging.
    self.lock.acquire()
    log.info("Tranferring tarballs to node: %s", node)
    self.lock.release()
    box = "%s@%s" % (self.deploy_user, node['automatic']['ipaddress_eth1'])

    # Deploy and untar code
    _push_and_untar(box, self.rc['code_tarball_location'],
        self.project['code_target_dir'])

    # Deploy and untar venv
    _push_and_untar(box, self.rc['venv_tarball_location'],
        self.project['venv_target_dir'])

    # Load the application into the virtual env
    venv_activate = "source %s/bin/activate" % self.project['venv_target_dir']
    pip_install = "pip install -e %s" % self.project['code_target_dir']
    run_as_subprocess('/usr/bin/ssh', box,
        '"%s && %s"' % (venv_activate, pip_install))

  def _activate(self):
    pool = Pool(min(len(self.nodes, MAX_NUM_WORKERS)))
    res = pool.map(self._activate_node, self.nodes)
    return res

  def _activate_node(self, node):
    box = "%s@%s" % (self.deploy_user, node['automatic']['ipaddress_eth1'])
    # Cut the code & venv symlinks over
    run_as_subprocess('/usr/bin/ssh', box,
        "'unlink /opt/%(pn)s/app && ln -s %(dir)s /opt/%(pn)s/app'"
        % {'pn': self.project['project_name'], 'dir': self.code_dir})
    run_as_subprocess('/usr/bin/ssh', box,
        "'unlink /opt/%(pn)s/app_virtual_env && " \
        "ln -s %(dir)s /opt/%(pn)s/app_virtual_env'"
        % {'pn': self.project['project_name'], 'dir': self.venv_dir})

    # Restart uwsgi
    raw_status = subprocess.check_output('/usr/bin/ssh', box,
        'supervisorctl status')
    process_list = raw_status.decode('utf8').split("\n")
    for row in process_list:
      if '%s:uwsgi' % self.project['project_name'] in row:
        match = re.search('pid (\d+)', row)
        if match:
          pid = match.group(1)
          run_as_subprocess('/usr/bin/ssh', box, "sudo kill -HUP %s" % pid)

    # Start all supervisor tasks <project>:task:*
    run_as_subprocess('/usr/bin/ssh', box,
        '"supervisorctl restart %s:task:*"' % self.project['project_name'])
    # TODO: run status again to check for errors
    return

  def load_node_list(self, roles, env):
    # Turn role list into node list
    role_clause = ' OR '.join(['role:%s' % r['chef_role_name'] for r in roles])
    chef_query = "chef_environment:%s AND (%s)" % (env['environment_name'],
        role_clause)
    self.nodes = self.chef_api.Search('node', chef_query)

  def _upload_static_assets_to_cdn():
    raise NotImplementedError
