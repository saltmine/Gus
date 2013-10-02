import logging
import yaml

import sqlcontext

#TODO: this should be in a config file
CONNECTION_ARGS = {
    'gus': {
      'prod': "dbname=gus user=postgres host=localhost",
      'test': "dbname=gus_test user=postgres host=localhost",
    }
}
CONFIG = {}

log = logging.getLogger(__name__)


def get_db_conn(dbname='gus'):
  '''return a production connection to the specified database
  '''
  log.info("connecting to production database")
  return sqlcontext.get_db_conn(CONNECTION_ARGS[dbname]['prod'])


def get_test_db_conn(dbname='gus'):
  '''return a test connection to the specified database
  '''
  log.info("connecting to test database")
  return sqlcontext.get_db_conn(CONNECTION_ARGS[dbname]['test'])


def load_from_file(file_handle):
  '''Load configuration from the given file
  '''
  global CONFIG
  CONFIG = yaml.load(file_handle)


def list_projects():
  '''Return a list of the configured projects.  Requires that a conifguration
  has already been loaded, e.g. via load_from_file
  '''
  return CONFIG.get('projects', {}).keys()


def get_tarball_dir(project_name):
  '''Return the tarball dir for the specified project
  '''
  return CONFIG.get('projects', {}).get(project_name, {}).get('tarball_dir')


def get_deploy_dir(project_name):
  '''Return the tarball dir for the specified project
  '''
  return CONFIG.get('projects', {}).get(project_name, {}).get('deploy_dir')


def get_venv_dir(project_name):
  '''Return the tarball dir for the specified project
  '''
  return CONFIG.get('projects', {}).get(project_name, {}).get('venv_dir')
