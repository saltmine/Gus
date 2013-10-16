'''
Database interface for the project model
'''

from lipstick.mget import mget, build_clauses
import gus.config

PUBLIC_FIELDS = (
    'project_id',
    'project_name',
    'date_created',
    'deploy_target_dir',
    'venv_target_dir',
)


def get_fields_for_sql(table_alias='p', count=False, ids_only=False):
  '''Generate standardized select list for queries
  '''
  if count:
    fields = "count(*) as cnt"
  elif ids_only:
    fields = "%s.project_id" % table_alias
  else:
    fields = ', '.join(["%s.%s" % (table_alias, field)
      for field in PUBLIC_FIELDS])
  return fields


def create_or_get(project_name):
  '''Create a new project entry
  '''
  with gus.config.get_db_conn().cursor(lock=project_name) as c:
    # The get happens in the same cursor because of the nesting magic
    project_info = get_by_name(project_name)
    if project_info is None:
      c.execute("""
          INSERT INTO projects (project_name)
          VALUES (%s)
          RETURNING project_id
          """, (project_name,))
      new_id = c.fetchone().project_id
    else:
      new_id = project_info['project_id']
  return new_id


def get_by_id(project_id):
  '''Look up a project by id
  '''
  fields = get_fields_for_sql()
  with gus.config.get_db_conn().cursor() as c:
    c.execute('''
        SELECT
          %s
        FROM
          projects p
        WHERE
          project_id=%%s
        ''' % fields, (project_id,))
    res = c.fetchone()
  return res


def get_by_name(project_name):
  '''Look up a proejct by name
  '''
  fields = get_fields_for_sql()
  with gus.config.get_db_conn().cursor() as c:
    c.execute('''
        SELECT
          %s
        FROM
          projects p
        WHERE
          project_name=%%s
        ''' % fields, (project_name,))
    res = c.fetchone()
  return res


def set_deploy_dir(project_id, deploy_dir):
  """Set the target dir to deploy to
  """
  query_vars = {'project_id': project_id, 'deploy_dir': deploy_dir}
  with gus.config.get_db_conn().cursor() as c:
    c.execute("""
        UPDATE
          projects
        SET
          deploy_target_dir=%(deploy_dir)s
        WHERE
          project_id=%(project_id)s
        """, query_vars)


def set_venv_dir(project_id, venv_dir):
  """Set the directory to deploy the venv to
  """
  query_vars = {'project_id': project_id, 'venv_dir': venv_dir}
  with gus.config.get_db_conn().cursor() as c:
    c.execute("""
        UPDATE
          projects
        SET
          venv_target_dir=%(venv_dir)s
        WHERE
          project_id=%(project_id)s
        """, query_vars)


@mget
def mget_all(count=False, ids_only=False, offset=None, limit=None):
  '''Return all projects, in date created order
  '''
  fields = get_fields_for_sql(count=count, ids_only=ids_only)
  page_clause, order_clause = build_clauses(count=count,
      default_order='project_id')
  query_vars = {'offset': offset, 'limit': limit}
  with gus.config.get_db_conn().cursor() as c:
    c.execute('''
        SELECT
          %s
        FROM
          projects p
        %s
        %s
        ''' % (fields, order_clause, page_clause), query_vars)
    res = c.fetchall()
  return res
