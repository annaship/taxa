# from sql_tables_class import MyConnection
# my_conn = MyConnection()
# my_conn = MyConnection(server_name="vampsdev")
# import sql_tables_class
# my_conn = sql_tables_class.MyConnection()

import MySQLdb
import sys
import shared #use shared to call connection from outside of the module
from pprint import pprint

class MyConnection:
  """
  Connection to env454
  Takes parameters from ~/.my.cnf, default host = "vampsdev", db="test"
  if different use my_conn = MyConnection(host, db)
  """
  def __init__(self, host="vampsdev", db="test"):
      self.conn   = None
      self.cursor = None
      self.rows   = 0
      self.new_id = None
      self.lastrowid = None
              
      try:
          print "=" * 40
          print "host = " + str(host) + ", db = "  + str(db)
          print "=" * 40

          self.conn   = MySQLdb.connect(host=host, db=db, read_default_file="~/.my.cnf")
          self.cursor = self.conn.cursor()
                 
      except MySQLdb.Error, e:
          print "Error %d: %s" % (e.args[0], e.args[1])
          raise
      except:                       # catch everything
          print "Unexpected:"         # handle unexpected exceptions
          print sys.exc_info()[0]     # info about curr exception (type,value,traceback)
          raise                       # re-throw caught exception   
  
  def close(self):
    if self.cursor:
      # print dir(self.cursor)
      self.cursor.close()
      self.conn.close()
      
 # def       
  
  def execute_fetch_select(self, sql):
      if self.cursor:
          self.cursor.execute(sql)
          res = self.cursor.fetchall ()
          return res

  def execute_no_fetch(self, sql):
      if self.cursor:
          self.cursor.execute(sql)
          self.conn.commit()
          return self.cursor.lastrowid

class SqlUtil:
    def __init__(self):
        pass
        

    # sql_tables_client.to_archive(table_list)
    def to_archive(self, table_list = ['tax_rdp_copy', 'tax_silva_taxonomy_copy']):
      """DROP all keys before using that!"""
      try: 
        for table_name in table_list:
          print "table = " + table_name
          shared.my_conn.cursor.execute ("DROP TABLE if exists copy")        
          shared.my_conn.cursor.execute ("CREATE TABLE copy LIKE %s" % (table_name))
          shared.my_conn.cursor.execute ("ALTER TABLE copy ENGINE=archive")
          shared.my_conn.cursor.execute ("INSERT IGNORE INTO copy SELECT * FROM %s" % (table_name))
          print "Number of rows affected: %d" % shared.my_conn.cursor.rowcount
          shared.my_conn.cursor.execute ("DROP TABLE if exists %s" % (table_name))
          shared.my_conn.cursor.execute ("RENAME TABLE copy TO %s" % (table_name))
          print "OK"
      except Exception, e:          # catch all deriving from Exception (instance e)
        print "Exception: ", e.__str__()      # address the instance, print e.__str__()
      except:                       # catch everything
        print "Unexpected:"         # handle unexpected exceptions
        print sys.exc_info()[0]     # info about curr exception (type,value,traceback)
        raise                       # re-throw caught exception   

    # sql_tables_client.to_show_keys(table_list)
    def to_show_keys(self, table_list):
      for table_name in table_list:
        shared.my_conn.connect ("show keys from %s" % (table_name))


    def change_name(self, table_list = []):
      """drop new_ in table names"""
      try: 
        for table_name in table_list:
          print "table = " + table_name
          shared.my_conn.cursor.execute ("ALTER TABLE ")

          shared.my_conn.cursor.execute ("DROP TABLE if exists copy")        
          shared.my_conn.cursor.execute ("CREATE TABLE copy LIKE %s" % (table_name))
          shared.my_conn.cursor.execute ("ALTER TABLE copy ENGINE=archive")
          shared.my_conn.cursor.execute ("INSERT IGNORE INTO copy SELECT * FROM %s" % (table_name))
          print "Number of rows affected: %d" % shared.my_conn.cursor.rowcount
          shared.my_conn.cursor.execute ("DROP TABLE if exists %s" % (table_name))
          shared.my_conn.cursor.execute ("RENAME TABLE copy TO %s" % (table_name))
          print "OK"
      except Exception, e:          # catch all deriving from Exception (instance e)
        print "Exception: ", e.__str__()      # address the instance, print e.__str__()
      except:                       # catch everything
        print "Unexpected:"         # handle unexpected exceptions
        print sys.exc_info()[0]     # info about curr exception (type,value,traceback)
        raise                       # re-throw caught exception   

