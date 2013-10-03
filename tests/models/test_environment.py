'''
Tests for environment database interface
'''

from nose.tools import eq_

import gus.config
from gus.models import environment
from lipstick.mget import MgetTestBase


class TestEnvironmentModel(object):
  '''Test the envrionment model setters & getters
  '''

  def setup(self):
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
    eq_(actual['environment_name'], self.environment_name)

  def test_get_by_name(self):
    '''Can look up an environment by it's name
    '''
    actual = environment.get_by_name(self.environment_name)
    eq_(actual['environment_id'], self.environment_id)

  def test_mget_all(self):
    '''Can get a list of all environments
    '''
    environment.create('stage')
    environment.create('prod')
    actual = environment.mget_all(offset=0, limit=10)
    eq_([env['environment_name'] for env in actual],
        [self.environment_name, 'stage', 'prod'])

  def test_set_hipchat_mode(self):
    '''Can set the hipchat mode for an environment
    '''
    for mode in ('off', 'quiet', 'all'):
      environment.set_hipchat_mode(self.environment_id, mode)
      actual = environment.get_by_id(self.environment_id)
      eq_(actual['hipchat_mode'], mode)


class TestMgetAll(MgetTestBase):
  '''Test that environment.mget_all conforms to the mget standard
  '''

  @classmethod
  def setup_class(cls):
    '''load data & set up expected results
    '''
    with gus.config.get_db_conn().cursor() as c:
      c.execute("TRUNCATE TABLE environments CASCADE")
    cls.expected_id_list = []
    cls.expected_id_list.append(environment.create('production'))
    cls.expected_id_list.append(environment.create('dev'))
    cls.expected_id_list.append(environment.create('testing'))
    cls.expected_object_list = [environment.get_by_id(eid)
        for eid in cls.expected_id_list]

  def __init__(self):
    '''Load the mget call to test
    '''
    self.mget_call = environment.mget_all
