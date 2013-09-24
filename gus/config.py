import logging

import sqlcontext

#TODO: this should be in a config file
CONNECTION_ARGS = {
    'gus': {
      'prod': "dbname=gus user=postgres host=localhost",
      'test': "dbname=gus_test user=postgres host=localhost",
    }
}

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
