"""
Tests for adding and querying chef roles
"""

from nose.tools import eq_

import gus.config
from gus.models import chef_role
from gus.models import project
from lipstick.mget import MgetTestBase


class TestChefRole(object):
  """Test createing and getting roles
  """

  def setup(self):
    """Clear out the db & create test role
    """
    # TODO: refactor database cleanup
    with gus.config.get_db_conn().cursor() as c:
      c.execute("TRUNCATE TABLE chef_roles, chef_roles_xref_projects CASCADE")
    self.role_name = 'www'
    self.role_id = chef_role.create(self.role_name, True)

  def test_get_by_id(self):
    """Can look up a configured chef role by its id
    """
    actual = chef_role.get_by_id(self.role_id)
    eq_(actual['chef_role_name'], self.role_name)

  def test_get_by_name(self):
    """Can look up a configured chef role by its name
    """
    actual = chef_role.get_by_name(self.role_name)
    eq_(actual['chef_role_id'], self.role_id)


class TestMgetAll(MgetTestBase):
  """Test mget spec for mget_all
  """
  def __init__(self):
    self.mget_call = chef_role.mget_all

  @classmethod
  def setup_class(cls):
    """Load test data
    """
    with gus.config.get_db_conn().cursor() as c:
      c.execute("TRUNCATE TABLE chef_roles, chef_roles_xref_projects CASCADE")
    cls.expected_id_list = []
    cls.expected_id_list.append(chef_role.create('www'))
    cls.expected_id_list.append(chef_role.create('admin'))
    cls.expected_id_list.append(chef_role.create('postgres'))
    cls.expected_id_list.append(chef_role.create('helios'))
    cls.expected_id_list.reverse()
    cls.expected_object_list = [chef_role.get_by_id(r_id)
        for r_id in cls.expected_id_list]


class TestMgetByProject(MgetTestBase):
  """Test mget spec for mget_all
  """
  def __init__(self):
    self.mget_call = chef_role.mget_by_project

  @classmethod
  def setup_class(cls):
    """Load test data
    """
    with gus.config.get_db_conn().cursor() as c:
      c.execute("TRUNCATE TABLE chef_roles, chef_roles_xref_projects CASCADE")
    project_id = project.create_or_get("outland")
    cls.expected_id_list = []
    cls.expected_id_list.append(chef_role.create('www'))
    cls.expected_id_list.append(chef_role.create('admin'))
    cls.expected_id_list.append(chef_role.create('postgres'))
    chef_role.create('helios')
    for role_id in cls.expected_id_list:
      chef_role.add_role_to_project(role_id, project_id)
    cls.expected_id_list.reverse()
    cls.expected_object_list = [chef_role.get_by_id(r_id)
        for r_id in cls.expected_id_list]
    cls.args = [project_id]
