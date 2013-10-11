"""
Database interface for the release candidate model
"""
import logging

from lipstick.mget import mget, build_clauses
import gus.config


log = logging.getLogger(__name__)

PUBLIC_FIELDS = (
    'release_candidate_id',
    'date_created',
    'project_id',
    'branch_name',
    'revision_id',
    'code_tarball_location',
    'venv_tarball_location',
)

ORDER_FIELDS = (
    'date_created',
)


def get_fields_for_sql(table_alias='rc', count=False, ids_only=False):
  """Generate standardized select list for queries
  """
  if count:
    fields = "count(*) as cnt"
  elif ids_only:
    fields = "%s.release_candidate_id" % table_alias
  else:
    fields = ', '.join(["%s.%s" % (table_alias, field)
      for field in PUBLIC_FIELDS])
  return fields


def create(project_id, branch_name, revision_id, code_tarball, venv_tarball):
  """Create a new release candidate
  """
  query_vars = {
      'project_id': project_id,
      'branch_name': branch_name,
      'revision_id': revision_id,
      'code_tarball': code_tarball,
      'venv_tarball': venv_tarball
  }
  lock_key = "create:%s:%s" % (project_id, revision_id)
  with gus.config.get_db_conn().cursor(lock=lock_key) as c:
    c.execute("""
        DELETE FROM
          release_candidates
        WHERE
          project_id = %(project_id)s
          AND
          revision_id = %(revision_id)s
        """, query_vars)
    c.execute("""
        INSERT INTO
          release_candidates (project_id, branch_name, revision_id,
          code_tarball_location, venv_tarball_location)
        VALUES
          (%(project_id)s, %(branch_name)s, %(revision_id)s,
          %(code_tarball)s, %(venv_tarball)s)
        RETURNING
          release_candidate_id
        """, query_vars)
    new_id = c.fetchone().release_candidate_id
  return new_id


def get_by_id(release_candidate_id):
  """Look up a release candidate by ID
  """
  fields = get_fields_for_sql()
  with gus.config.get_db_conn().cursor() as c:
    c.execute("""
        SELECT
          %s
        FROM
          release_candidates rc
        WHERE
          release_candidate_id = %%s
        """ % fields, (release_candidate_id,))
    res = c.fetchone()
  return res


def get_by_project_revision(project_id, revision_id):
  """Look up a release candidate by project and revision
  """
  fields = get_fields_for_sql()
  query_vars = {'project_id': project_id, 'revision_id': revision_id}
  with gus.config.get_db_conn().cursor() as c:
    c.execute("""
        SELECT
          %s
        FROM
          release_candidates rc
        WHERE
          project_id = %%(project_id)s
          AND
          revision_id = %%(revision_id)s
        """ % fields, query_vars)
    res = c.fetchone()
  return res


@mget
def mget_by_project(project_id, count=False, limit=None, offset=None,
    ids_only=False):
  """Get all release candidates for the given project
  """
  page_clause, order_clause = build_clauses(count, order_by='date_created',
      valid_orders=ORDER_FIELDS)
  fields = get_fields_for_sql(count=count, ids_only=ids_only)
  query_vars = {'project_id': project_id, 'limit': limit, 'offset': offset}
  with gus.config.get_db_conn().cursor() as c:
    query = """
        SELECT
          %s
        FROM
          release_candidates rc
        WHERE
          project_id = %%(project_id)s
        %s
        %s
        """ % (fields, order_clause, page_clause)
    c.execute(query, query_vars)
    res = c.fetchall()
  return res


@mget
def mget_by_project_branch(project_id, branch_name, count=False, limit=None,
    offset=None, ids_only=False):
  """Get all release candidates for the given project and branch
  """
  page_clause, order_clause = build_clauses(count)
  fields = get_fields_for_sql(count=count, ids_only=ids_only)
  query_vars = {'project_id': project_id, 'branch_name': branch_name,
      'offset': offset, 'limit': limit}
  with gus.config.get_db_conn().cursor() as c:
    query = """
        SELECT
          %s
        FROM
          release_candidates rc
        WHERE
          project_id = %%(project_id)s
          AND
          branch_name = %%(branch_name)s
        %s
        %s""" % (fields, order_clause, page_clause)
    c.execute(query, query_vars)
    res = c.fetchall()
  return res
