'''
Database interface for the project model
'''

import gus.config

PUBLIC_FIELDS = ('project_id', 'project_name', 'date_created',)


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


def create(project_name):
  '''Create a new project entry
  '''
  with gus.config.get_db_conn().cursor() as c:
    c.execute("""
        INSERT INTO projects (project_name)
        VALUES (%s)
        RETURNING project_id
        """, (project_name,))
    new_id = c.fetchone().project_id
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


def mget_all():
  '''Return all projects, in date created order
  '''
  fields = get_fields_for_sql()
  with gus.config.get_db_conn().cursor() as c:
    c.execute('''
        SELECT
          %s
        FROM
          projects p
        ''' % fields)
    res = c.fetchall()
  return res
