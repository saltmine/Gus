'''
Tests for project database interface
'''

from nose.tools import eq_

from lipstick.mget import MgetTestBase
import gus.config
from gus.models import project


class TestProjectModel(object):
  '''Basic getter & setter tests for the project model
  '''

  def setup(self):
    '''Clear out the database & create a test project
    '''
    # TODO: refactor database cleanup
    self.db_conn = gus.config.get_db_conn()
    with self.db_conn.cursor() as c:
      c.execute("TRUNCATE TABLE projects CASCADE")
    self.project_name = "frobnitz"
    self.project_id = project.create_or_get(self.project_name)

  def test_get_by_id(self):
    '''Can look up a project by project_id
    '''
    actual = project.get_by_id(self.project_id)
    eq_(actual['project_name'], self.project_name)

  def test_get_by_name(self):
    '''Can look up a project by project name
    '''
    actual = project.get_by_name(self.project_name)
    eq_(actual['project_id'], self.project_id)

  def test_mget_all(self):
    '''Can get a list of all projects in ordered by create date
    '''
    project.create_or_get("foo")
    project.create_or_get("bar")
    actual = project.mget_all(offset=0, limit=10)
    eq_(len(actual), 3)
    eq_([p['project_name'] for p in actual], [self.project_name, 'foo', 'bar'])

  def test_duplicate_create(self):
    """Trying to create an existing project just returns the existing project
    """
    new_id = project.create_or_get(self.project_name)
    eq_(new_id, self.project_id)

  def test_set_and_get_deploy_dir(self):
    """Can set and get the deploy dir for a project
    """
    before = project.get_by_id(self.project_id)
    eq_(before['deploy_target_dir'], None, "GUARD: Deploy dir set at start")
    deploy_dir = '/opt/outland/app/'
    project.set_deploy_dir(self.project_id, deploy_dir)
    after = project.get_by_id(self.project_id)
    eq_(after['deploy_target_dir'], deploy_dir)

  def test_set_and_get_venv_dir(self):
    """Can set and get the venv dir for a project
    """
    before = project.get_by_id(self.project_id)
    eq_(before['venv_target_dir'], None, "GUARD: venv dir set at start")
    venv_dir = '/opt/outland/app/'
    project.set_venv_dir(self.project_id, venv_dir)
    after = project.get_by_id(self.project_id)
    eq_(after['venv_target_dir'], venv_dir)


class TestMgetAllProject(MgetTestBase):
  '''Test that project.mget_all conforms to the mget standard
  '''

  @classmethod
  def setup_class(cls):
    '''Load data and record expected results
    '''
    with gus.config.get_db_conn().cursor() as c:
      c.execute("TRUNCATE TABLE projects CASCADE")
    cls.expected_id_list = []
    cls.expected_id_list.append(project.create_or_get('foo'))
    cls.expected_id_list.append(project.create_or_get('bar'))
    cls.expected_id_list.append(project.create_or_get('baz'))
    cls.expected_object_list = [project.get_by_id(pid)
        for pid in cls.expected_id_list]

  def __init__(self):
    '''Load the mget function here
    '''
    self.mget_call = project.mget_all
