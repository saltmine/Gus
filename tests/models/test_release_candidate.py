"""
Tests for release candidate database interface
"""

from nose.tools import eq_

from lipstick.mget import MgetTestBase
import gus.config
from gus.models import project
from gus.models import release_candidate


class TestReleaseCandidateModel(object):
  """
  Test basic operations of the release candidate model
  """

  def setup(self):
    '''Clear out the database & create a test project
    '''
    # TODO: refactor database cleanup
    self.db_conn = gus.config.get_db_conn()
    with self.db_conn.cursor() as c:
      c.execute("TRUNCATE TABLE projects, release_candidates CASCADE")
    self.project_name = "frobnitz"
    self.project_id = project.create(self.project_name)
    self.revision = '82a44ae623c6d60ba43cc49c50599f7a3f63a445'
    self.code_tarball = \
        '/opt/builds/gus/82a44ae623c6d60ba43cc49c50599f7a3f63a445.tgz'
    self.venv_tarball = '/opt/builds/gus/some_env.tgz'
    self.rc_id = release_candidate.create(self.project_id, 'master',
        self.revision, self.code_tarball, self.venv_tarball)

  def test_get_by_id(self):
    """Can look up a release candidate by id
    """
    actual = release_candidate.get_by_id(self.rc_id)
    eq_(actual['project_id'], self.project_id)
    eq_(actual['revision_id'], self.revision)

  def test_duplicate_builds(self):
    """Registering an existing build overwrites the old release candidate
    """
    before_count = release_candidate.mget_by_project(self.project_id,
        count=True)
    eq_(before_count, 1,
        "GUARD: Found more than one initial release candidates")
    new_code = '/new/tarball/path'
    new_venv = '/new/venv/path'
    self.rc_id = release_candidate.create(self.project_id, 'master',
        self.revision, new_code, new_venv)
    after = release_candidate.get_by_project_revision(self.project_id,
        self.revision)
    eq_(after['code_tarball_location'], new_code)
    eq_(after['venv_tarball_location'], new_venv)
    after_count = release_candidate.mget_by_project(self.project_id,
        count=True)
    eq_(after_count, 1, "Multiple entries created for project")

  def test_get_by_project_revision(self):
    """Can look up a release candidate by project & revision
    """
    actual = release_candidate.get_by_project_revision(self.project_id,
        self.revision)
    eq_(actual['release_candidate_id'], self.rc_id)
    eq_(actual['code_tarball_location'], self.code_tarball)


class TestMgetByProject(MgetTestBase):
  """Test getting all release candidates for a given project
  """
  def __init__(self):
    self.mget_call = release_candidate.mget_by_project

  @classmethod
  def setup_class(cls):
    with gus.config.get_db_conn().cursor() as c:
      c.execute("TRUNCATE TABLE projects, release_candidates CASCADE")
    project_name = "frobnitz"
    project_id = project.create(project_name)
    cls.expected_id_list = []
    cls.expected_id_list.append(release_candidate.create(project_id, 'master',
      'abc123', '/some/path.tar', '/other/path.tar'))
    cls.expected_id_list.append(release_candidate.create(project_id, 'master',
      'deadbeef', '/some/path.tar', '/other/path.tar'))
    cls.expected_id_list.append(release_candidate.create(project_id, 'feature',
      'aeff234', '/some/path.tar', '/other/path.tar'))
    # Newest first order by default
    cls.expected_id_list.reverse()
    cls.expected_object_list = [release_candidate.get_by_id(rc_id)
        for rc_id in cls.expected_id_list]
    cls.args = (project_id,)

class TestMgetByProjectBranch(MgetTestBase):
  """Test getting all release candidates for a given project and branch
  """
  def __init__(self):
    self.mget_call = release_candidate.mget_by_project_branch

  @classmethod
  def setup_class(cls):
    with gus.config.get_db_conn().cursor() as c:
      c.execute("TRUNCATE TABLE projects, release_candidates CASCADE")
    project_name = "frobnitz"
    project_id = project.create(project_name)
    cls.expected_id_list = []
    cls.expected_id_list.append(release_candidate.create(project_id, 'master',
      'abc123', '/some/path.tar', '/other/path.tar'))
    cls.expected_id_list.append(release_candidate.create(project_id, 'master',
      'deadbeef', '/some/path.tar', '/other/path.tar'))
    # create a release candidate in another branch that we don't expect to get
    # back
    release_candidate.create(project_id, 'feature', 'aeff234', '/some/path.tar',
        '/other/path.tar')
    cls.expected_object_list = [release_candidate.get_by_id(rc_id)
        for rc_id in cls.expected_id_list]
    cls.args = (project_id, 'master')
