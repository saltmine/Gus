'''
Tests for project database interface
'''

import unittest

import gus.config
from gus.models import project


class TestProjectModel(unittest.TestCase):
  '''Basic getter & setter tests for the project model
  '''

  def setUp(self):
    '''Clear out the database & create a test project
    '''
    # TODO: refactor database cleanup
    self.db_conn = gus.config.get_db_conn()
    with self.db_conn.cursor() as c:
      c.execute("TRUNCATE TABLE projects CASCADE")
    self.project_name = "frobnitz"
    self.project_id = project.create(self.project_name)

  def test_get_by_id(self):
    '''Can look up a project by project_id
    '''
    actual = project.get_by_id(self.project_id)
    self.assertEquals(actual['project_name'], self.project_name)

  def test_get_by_name(self):
    '''Can look up a project by project name
    '''
    actual = project.get_by_name(self.project_name)
    self.assertEquals(actual['project_id'], self.project_id)

  def test_mget_all(self):
    '''Can get a list of all projects in ordered by create date
    '''
    project.create("foo")
    project.create("bar")
    actual = project.mget_all()
    self.assertEquals(len(actual), 3)
    self.assertEquals([p['project_name'] for p in actual],
        [self.project_name, 'foo', 'bar'])
