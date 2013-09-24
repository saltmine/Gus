"""
Scripts for working with the database
"""
import os
import sys


def nuke(test_db=True, username='postgres'):
  '''Destroy and re-create the database.  Should only be used for dev.
  '''
  import subprocess
  # TODO: read this from a config...
  if test_db:
    db_name = 'gus_test'
  else:
    db_name = 'gus'
  cmd = ['dropdb', db_name, '-U', username]
  print " ".join(cmd)
  subprocess.call(cmd)
  cmd = ['createdb', db_name, '-E', 'utf8', '-U', username, '-T',
    'template0', '-h', 'localhost']
  print " ".join(cmd)
  subprocess.call(cmd)


def update_db(test_db=False):
  '''Updates the DB to the latest version available in the sql directory'''
  import pkg_resources

  if test_db:
    db_conn = watson.database.get_test_db_conn()
  else:
    db_conn = watson.database.get_db_conn()

  bootstrap_code = pkg_resources.resource_string('watson', 'sql/bootstrap.sql')
  migration_files = []
  code_files = []
  try:
    migration_files = pkg_resources.resource_listdir('watson', 'sql/migrations')
  except OSError:
    print "WARNING - No SQL migration files were found. If you haven't "\
        "written any yet, you can ignore this warning"

  try:
    code_files = pkg_resources.resource_listdir('watson', 'sql/code')
  except OSError:
    print "WARNING - No SQL code files were found. If you haven't written "\
        "any yet, you can ignore this warning"

  # set versions to be a sorted list of all of the scripts that start with
  # three digits.
  migrations = sorted([f for f in migration_files if f[:3].isdigit()])

  current_version = 0
  # TODO: Deal with read/write split
  with db_conn.cursor() as c:
    #check if we have nothing in the DB -
    c.execute("""
        SELECT
          tablename
        FROM
          pg_tables
        WHERE
          tablename NOT LIKE 'pg_%'
          AND
          tablename NOT LIKE 'sql_%'
      """)
    tables = [result.tablename for result in c.fetchall()]
    if not tables:
      #run the bootstrap script
      c.execute(bootstrap_code)
      print "bootstrap ran %s rows affected" % c.rowcount
      c.execute("INSERT INTO versions VALUES (%s, %s, NOW())",
          (-1, 0))
    if 'versions' in tables:
      c.execute("select COALESCE(MAX(to_version), 0) v from versions")
      current_version = c.fetchone().v

  #do all the schema updates
  for f in migrations:
    new_version = int(f[:3])
    if current_version < new_version:
      #run the upgrade
      guts = pkg_resources.resource_string('watson', 'sql/migrations/%s' % f)
      with db_conn.cursor() as c:
        print "executing upgrade script %s" % f
        c.execute(guts)
        c.execute("INSERT INTO versions VALUES (%s, %s, NOW())",
            (current_version, new_version))
        current_version = new_version

  #now do all stored procedures
  for f in code_files:
    script_guts = pkg_resources.resource_string('watson', 'sql/code/%s' % f)
    with db_conn.cursor() as c:
      print "executing code script %s" % f
      c.execute(script_guts)


if __name__ == "__main__":
  ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(
                              os.path.abspath(__file__)), "../.."))
  if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH)
  print "sys path is %s" % sys.path
  update_db()
