'''
Tests for environment database interface
'''

import unittest

import gus.config
from gus.models import environment


class TestEnvironmentModel(unittest.TestCase):
  '''Test the envrionment model setters & getters
  '''

  def setUp(self):
    '''Clear out the database & create a test project
    '''
    # TODO: refactor database cleanup
    self.db_conn = gus.config.get_db_conn()
    with self.db_conn.cursor() as c:
      c.execute("TRUNCATE TABLE environments CASCADE")
    self.environment_name = 'dev'
    self.environment_id = environment.create(self.environment_name)

  def test_get_by_id(self):
    '''Can look up an environment by it's id
    '''
    actual = environment.get_by_id(self.environment_id)
    self.assertEquals(actual['environment_name'], self.environment_name)

  def test_get_by_name(self):
    '''Can look up an environment by it's name
    '''
    actual = environment.get_by_name(self.environment_name)
    self.assertEquals(actual['environment_id'], self.environment_id)

  def test_mget_all(self):
    '''Can get a list of all environments
    '''
    environment.create('stage')
    environment.create('prod')
    actual = environment.mget_all()
    self.assertEquals([env['environment_name'] for env in actual],
        [self.environment_name, 'stage', 'prod'])

  def test_set_hipchat_mode(self):
    '''Can set the hipchat mode for an environment
    '''
    for mode in ('off', 'quiet', 'all'):
      environment.set_hipchat_mode(self.environment_id, mode)
      actual = environment.get_by_id(self.environment_id)
      self.assertEquals(actual['hipchat_mode'], mode)
