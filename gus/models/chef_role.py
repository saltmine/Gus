"""
Model for recording information about chef roles
"""

from lipstick.mget import mget, build_clauses

import gus.config
PUBLIC_FIELDS = (
    'chef_role_id',
    'chef_role_name',
    'serial_deploy',
    'date_created',
)

ORDER_FIELDS = (
    'date_created',
)


def get_fields_for_sql(table_alias='cr', count=False, ids_only=False):
  """Generate the field list for select statements
  """
  if count:
    fields = "count(*) as cnt"
  elif ids_only:
    fields = "%s.chef_role_id" % table_alias
  else:
    fields = ', '.join(["%s.%s" % (table_alias, field)
      for field in PUBLIC_FIELDS])
  return fields


def create(role_name, serial_flag=False):
  """Create a new chef role
  """
  query_vars = {'role_name': role_name, 'serial_flag': serial_flag}
  with gus.config.get_db_conn().cursor() as c:
    c.execute("""
        INSERT INTO
          chef_roles (chef_role_name, serial_deploy)
        VALUES
          (%(role_name)s, %(serial_flag)s)
        RETURNING chef_role_id
        """, query_vars)
    new_id = c.fetchone().chef_role_id
  return new_id


def get_by_id(role_id):
  """get a chef role by id
  """
  fields = get_fields_for_sql()
  with gus.config.get_db_conn().cursor() as c:
    c.execute("""
        SELECT
          %s
        FROM
          chef_roles cr
        WHERE
          chef_role_id = %%s
        """ % fields, (role_id,))
    res = c.fetchone()
  return res


def get_by_name(role_name):
  """get a chef role by name
  """
  fields = get_fields_for_sql()
  with gus.config.get_db_conn().cursor() as c:
    c.execute("""
        SELECT
          %s
        FROM
          chef_roles cr
        WHERE
          chef_role_name = %%s
        """ % fields, (role_name,))
    res = c.fetchone()
  return res


def add_role_to_project(role_id, project_id):
  """add a mapping for the given role to the given project, indicating that
  a deploy of that project should include the specified role
  """
  query_vars = {'role_id': role_id, 'project_id': project_id}
  with gus.config.get_db_conn().cursor() as c:
    c.execute("""
        INSERT INTO
          chef_roles_xref_projects (project_id, chef_role_id)
        VALUES
          (%(project_id)s, %(role_id)s)
        """, query_vars)


@mget
def mget_all(offset=None, limit=None, count=False, ids_only=False):
  """Get a list of all configured roles
  """
  page_clause, order_clause = build_clauses(count, order_by='date_created',
      valid_orders=ORDER_FIELDS)
  fields = get_fields_for_sql(count=count, ids_only=ids_only)
  query_vars = {'offset': offset, 'limit': limit}
  with gus.config.get_db_conn().cursor() as c:
    c.execute("""
        SELECT
          %s
        FROM
          chef_roles cr
        %s
        %s """ % (fields, order_clause, page_clause), query_vars)
    res = c.fetchall()
  return res


@mget
def mget_by_project(project_id, offset=None, limit=None, count=False,
    ids_only=False):
  """Get a list of all roles the given project is associated with
  """
  page_clause, order_clause = build_clauses(count, order_by='date_created',
      valid_orders=ORDER_FIELDS)
  fields = get_fields_for_sql(count=count, ids_only=ids_only)
  query_vars = {'offset': offset, 'limit': limit, 'project_id': project_id}
  with gus.config.get_db_conn().cursor() as c:
    c.execute("""
        SELECT
          %s
        FROM
          chef_roles cr
          JOIN chef_roles_xref_projects x ON (x.chef_role_id = cr.chef_role_id)
        WHERE
          x.project_id = %%(project_id)s
        %s
        %s """ % (fields, order_clause, page_clause), query_vars)
    res = c.fetchall()
  return res
