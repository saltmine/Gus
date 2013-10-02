'''Tools for managing deploys
'''
from newman import Newman

from .scripts import database


def main():
  n = Newman("Automation tools for deploys and related information")
  n.load_module(database, 'database')
  n.go()
