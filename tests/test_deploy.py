from nose.tools import eq_, ok_, assert_raises
from mock import patch, Mock

from gus.lib import deploy

@patch('gus.lib.deploy.chef.DataBag')
def test_available_app(DataBag_mock):
  """Valid app loads configuration info from chef.
  """
  DataBag_mock.return_value = {
    'projects': {
      'valid_app': {}
    }
  }
  api = Mock()
  d = deploy.Deploy('valid_app', 'revfoo', chef_api=api)
  ok_(d.load(), "Chef config has loaded")



@patch('gus.lib.deploy.chef.DataBag')
def test_nonexistent_app(DataBag_mock):
  """A non-existent app raises an error.
  """
  DataBag_mock.return_value = {
    'projects': {
      'valid_app': {}
    }
  }
  api = Mock()
  d = deploy.Deploy('invalid_app', 'revfoo', chef_api=api)
  assert_raises(ValueError, d.load)
