#! /opt/local/bin/python

import sql_tables_class
import sys
import shared
from datetime import datetime, timedelta

class BackupSubmit:
    """
        Delete backups older then 7 days from submission tables.
    """

    def __init__(self):
        self.how_old         = 7 #days
        self.date_N_days_ago = datetime.now() - timedelta(days=self.how_old)

    def get_submit_codes(self):
        sql = 'SELECT DISTINCT submit_code FROM vamps_submissions WHERE submit_code LIKE "%\_backup\_%"'
        res  = shared.my_conn.execute_fetch_select(sql)    
        return res
        
    def get_dates(self):
        submit_codes_to_del = [] 
        submit_codes        = self.get_submit_codes()
        for submit_code in submit_codes:
           backup_date = submit_code[0].split('_backup_')[1]
           if self.old_date(backup_date):
               submit_codes_to_del.append(submit_code[0])
        return submit_codes_to_del

    def old_date(self, long_date):
        backup_date = datetime.strptime(long_date, "%Y%m%d%H%M%S")    
        if backup_date < self.date_N_days_ago:
            return True #DELETE!
            
    def delete_old_backups(self, submit_codes_to_del):
        submit_codes_to_del_str = "'" + "', '".join(submit_codes_to_del) + "'"
        sql1 = "DELETE FROM vamps_submissions_tubes WHERE submit_code in (%s)" % submit_codes_to_del_str
        sql2 = "DELETE FROM vamps_submissions       WHERE submit_code in (%s)" % submit_codes_to_del_str
        print sql1
        res  = shared.my_conn.execute_no_fetch(sql1)    

        print sql2
        res  = shared.my_conn.execute_no_fetch(sql2)    
        
        
if __name__ == '__main__':
  # shared.my_conn = sql_tables_class.MyConnection('vampsdev', 'vamps2') 
  shared.my_conn = sql_tables_class.MyConnection('vampsdb', 'vamps')
  submit_codes_to_del = BackupSubmit().get_dates()
  BackupSubmit().delete_old_backups(submit_codes_to_del)  
