#services 
from utilities.db_utils import DatabaseUtility
class userverificationservice:
    def __init__(self):
        self.db_util=DatabaseUtility()
    
    def verify_user(self,email):
        with self.db_util as db:
            query_result = db.execute_query("Select CustomerID,FullName from CustomerData where Email=?",(email))
            custid = 0
            fullname = ''
            if query_result is not None:
                for row in query_result:
                    custid=row['CustomerID']
                    fullname=row['FullName']
                    
            return custid,fullname
                    
        
            
        
    