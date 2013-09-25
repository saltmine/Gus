import logging

from multiprocessing.dummy import Pool, Lock
import chef

MAX_NUM_WORKERS = 4

log = logging.getLogger('gus.lib.deploy')


class Deploy(object):
  def __init__(self, app, revision, chef_api=None):
    self.app = app
    self.revision = revision
    self.chef_api = chef_api
    self.chef_app_prefs = None
    self.nodes = None

    self.lock = Lock()

  def load(self):
    """Load application config from Chef data bag.
    """
    bag = chef.DataBag('projects', api=self.chef_api)
    item = bag['projects']
    try:
      self.chef_app_prefs = item[self.app]
    except KeyError:
      raise ValueError("Application '%s' does not exist in Chef" % self.app)

    return True

  @property
  def available_roles(self):
    """Get the list of available roles for this application. Roles are optional
    and the lack of them should return an empty list in which case every node
    can be deployed to. Throws if the app config hasn't been loaded from chef.
    """
    if self.chef_app_prefs is None:
      raise RuntimeError("Application must be loaded from chef")
    try:
      return set(self.chef_app_prefs['roles'])
    except KeyError:
      return set()

  def deploy(self, env=None, roles=None):
    """Perform a deploy.
    """
    # does this app_rev exist for this app?
    #dn = chef.Node('dev-monitor-001', api=self.chef_api)

    # Are the roles valid?
    roles = set(roles)
    if (roles | self.available_roles) != self.available_roles:
      raise RuntimeError("Attempting to deploy to invalid role: %s" % (
        roles - self.available_roles))

    # can we deploy app to these nodes?

    # turn app:app_rev into tarball url
    # turn app_app_rev into venv url

    # if nodes include roles with static assets:
      # upload static assets

    # transfer tarballs to servers
    self._transfer()

    # Does this app interface with a db?
      # do we need to run a migration?
        # activate() on role('migration')

    # activate on all machines
    self._activate()

  def _transfer(self):
    pool = Pool(min(len(self.nodes, MAX_NUM_WORKERS)))
    res = pool.map(self._transfer_to_node, self.nodes)

  def _transfer_to_node(self, node):
    self.lock.acquire()
    log.info("Tranferring tarballs to node: %s", node)
    self.lock.release()
    # TODO

  def _activate(self):
    # if we are serializing deploy
      # todo
    # for each node:
      # is it consumer facing and attached to lb
        # check if there is more than one node attached to lb, raise if not
        # detach from lb
        # activate node
        # attach to lb
    pool = Pool(min(len(self.nodes, MAX_NUM_WORKERS)))
    res = pool.map(self._activate_node, self.nodes)

  def _activate_node(self, node):
    return

  # def reload_config():
  def get_nodes(self):
    return

if __name__ == "__main__":
  api = chef.ChefAPI('https://chef.keep.dev', '.chef/user.pem', 'ryan')

  d = Deploy('outland', '2241acc7965514bfd99e49305840816fc182212b',
             chef_api=api)
  d.load()
  print d.available_roles
  d.deploy(env='dev', roles=['www'])
