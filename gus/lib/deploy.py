import logging
import os.path

from multiprocessing.dummy import Pool, Lock
import subprocess
import chef

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


class Deploy(object):
  def __init__(self, release_candidate_id, chef_api=None):
    self.chef_api = chef_api
    self.chef_app_prefs = None

    # turn app:app_rev into tarball url
    self.rc = release_candidate.get_by_id(release_candidate_id)
    self.project = project.get_by_id(self.rc['project_id'])
    self.lock = Lock()
    self.nodes = []

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
    if not os.path.isfile(self.rc['code_tarball_location']):
      return None
    if not os.path.isfile(self.rc['venv_tarball_location']):
      return None

    #dn = chef.Node('dev-monitor-001', api=self.chef_api)

    # Are the roles valid?
    target_role_names = set([r['chef_role_name'] for r in roles])
    available_role_names = set([r['chef_role_name']
      for r in self.available_roles])
    if (target_role_names | available_role_names) != available_role_names:
      raise RuntimeError("Attempting to deploy to invalid role: %s" % (
        target_role_names - available_role_names))

    # Turn role list into node list
    role_clause = ' OR '.join(['role:%s' % r['chef_role_name'] for r in roles])
    chef_query = "chef_environment:%s AND (%s)" % (env['environment_name'],
        role_clause)
    self.nodes = self.chef_api.Search('node', chef_query)
    # can we deploy app to these nodes?
    if not self.nodes:
      return None

    # TODO: Upload static assets
    #if 'www' in roles:
      #self.upload_static_assets_to_cdn()

    # transfer tarballs to servers
    self._transfer()

    # TODO: Database migrations? Other scripts? Pip activate?
    # Does this app interface with a db?
      # do we need to run a migration?
        # activate() on role('migration')

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

  def _transfer_to_node(self, node, deploy_user='outland'):
    # Logging doesn't play nicely with multi-processing, so lock before
    # logging.
    self.lock.acquire()
    log.info("Tranferring tarballs to node: %s", node)
    self.lock.release()
    box = "%s@%s" % (deploy_user, node['automatic']['ipaddress_eth1'])

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
    # if we are serializing deploy
      # TODO
    # for each node:
      # is it consumer facing and attached to lb
        # check if there is more than one node attached to lb, raise if not
        # detach from lb
        # activate node
        # attach to lb
    pool = Pool(min(len(self.nodes, MAX_NUM_WORKERS)))
    res = pool.map(self._activate_node, self.nodes)
    return res

  def _activate_node(self, node):
    raise NotImplementedError
    return

  # def reload_config():
  def get_nodes(self):
    raise NotImplementedError
    return

  def _upload_static_assets_to_cdn():
    raise NotImplementedError

if __name__ == "__main__":
  api = chef.ChefAPI('https://chef.keep.dev', '.chef/user.pem', 'ryan')

  d = Deploy('outland', '2241acc7965514bfd99e49305840816fc182212b',
             chef_api=api)
  d.load()
  print d.available_roles
  d.deploy(env='dev', roles=['www'])
