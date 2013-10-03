'''
Magically connect to the test database
'''
import gus.config

gus.config.get_db_conn = gus.config.get_test_db_conn
