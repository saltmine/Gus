'''
Tests for loading and accessing the configuration
'''
from StringIO import StringIO
import unittest

import gus.config


class TestConfig(unittest.TestCase):
  '''Config tests
  '''

  def setUp(self):
    '''Initilize the config
    '''
    config_file = StringIO('''
      projects:
        helios:
          tarball_dir: '/opt/helios/builds/'
          deploy_dir: '/opt/helios/'
          venv_dir: '/opt/helios/venvs/'
        outland:
          tarball_dir: '/opt/outland/builds/'
          deploy_dir: '/opt/outland/'
          venv_dir: '/opt/outland/venvs/'
        watson:
          tarball_dir: '/opt/watson/builds/'
          deploy_dir: '/opt/watson/'
          venv_dir: '/opt/watson/venvs/'
      ''')
    gus.config.load_from_file(config_file)

  def test_list_projects(self):
    '''Can get a list of the configured projects
    '''
    # Don't care about order, so turn these into a set
    actual = set(gus.config.list_projects())
    expected = set(['helios', 'outland', 'watson'])
    self.assertEquals(actual, expected)

  def test_get_tarball_dir(self):
    '''Can get the tarball directory for a given project
    '''
    expected = '/opt/helios/builds/'
    actual = gus.config.get_tarball_dir('helios')
    self.assertEquals(actual, expected)

  def test_get_deploy_dir(self):
    '''Can get the deploy directory for a given project
    '''
    expected = '/opt/helios/'
    actual = gus.config.get_deploy_dir('helios')
    self.assertEquals(actual, expected)

  def test_get_venv_dir(self):
    '''can get the venv dir for a project
    '''
    expected = '/opt/watson/venvs/'
    actual = gus.config.get_venv_dir('watson')
    self.assertEquals(expected, actual)
