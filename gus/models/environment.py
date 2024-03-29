'''
Database interface for the environment model
'''
import logging

import gus.config
from lipstick.mget import mget, build_clauses

log = logging.getLogger(__name__)

PUBLIC_FIELDS = ('environment_id',
    'environment_name',
    'hipchat_mode',
    'date_created',
)


def get_fields_for_sql(table_alias='e', count=False, ids_only=False):
  '''generate standard field list for sql
  '''
  if count:
    fields = "count(*) as cnt"
  elif ids_only:
    fields = "%s.environment_id" % table_alias
  else:
    fields = ', '.join(["%s.%s" % (table_alias, field)
      for field in PUBLIC_FIELDS])
  return fields


def create(name, hipchat_mode='off'):
  '''Create a new environment
  '''
  with gus.config.get_db_conn().cursor() as c:
    c.execute("""
        INSERT INTO
          environments (environment_name, hipchat_mode)
        VALUES
          (%s, %s)
        RETURNING environment_id
        """, (name, hipchat_mode))
    new_id = c.fetchone().environment_id
  return new_id


def get_by_id(environment_id):
  '''Look up an environment by id
  '''
  fields = get_fields_for_sql()
  with gus.config.get_db_conn().cursor() as c:
    c.execute("""
        SELECT
          %s
        FROM
          environments e
        WHERE
          environment_id=%%s
        """ % fields, (environment_id,))
    res = c.fetchone()
  return res


def get_by_name(environment_name):
  '''Look up an environment by name
  '''
  fields = get_fields_for_sql()
  with gus.config.get_db_conn().cursor() as c:
    c.execute("""
        SELECT
          %s
        FROM
          environments e
        WHERE
          environment_name=%%s
        """ % fields, (environment_name,))
    res = c.fetchone()
  return res


@mget
def mget_all(offset=None, limit=None, count=False, ids_only=False):
  '''List all environments
  '''
  fields = get_fields_for_sql(count=count, ids_only=ids_only)
  page_clause, order_clause = build_clauses(count=count,
      default_order='environment_id')
  query_vars = {'offset': offset, 'limit': limit}
  with gus.config.get_db_conn().cursor() as c:
    c.execute("""
        SELECT
          %s
        FROM
          environments e
        %s
        %s
        """ % (fields, order_clause, page_clause), query_vars)
    res = c.fetchall()
  return res


def set_hipchat_mode(environment_id, hipchat_mode):
  '''Set the hipchat alert mode for the given environment
  '''
  with gus.config.get_db_conn().cursor() as c:
    c.execute("""
        UPDATE
          environments
        SET
          hipchat_mode=%s
        WHERE
          environment_id=%s
        """, (hipchat_mode, environment_id))
