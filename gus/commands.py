"""Tools for managing deploys
"""
from newman import Newman

from .scripts import database
from .scripts import register


def main():
  """Load CLI functions from script modules
  """
  newman = Newman("Automation tools for deploys and related information")
  newman.load_module(database, 'database')
  newman.load_module(register, 'register')
  newman.go()
