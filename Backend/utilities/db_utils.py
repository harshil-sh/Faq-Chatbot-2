# db_utils.py
import pyodbc
import json

class DatabaseUtility:
    def __init__(self):
        self.connection_string = self.get_connection_string()
        self.connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    def get_connection_string(self):
        with open('config.json') as f:
            config = json.load(f)
            return config["connectionstring"]

    def connect(self):
        if self.connection is None:
            self.connection = pyodbc.connect(self.connection_string)

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def insert_or_update_data(self, query, params):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
        except Exception as error:
            print("Exception:", error)
            self.connection.rollback()
        finally:
            cursor.close()
    def execute_query(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            rows = cursor.fetchall()
        except Exception as error:
            print("Exception: ",error) 
        finally:  
            cursor.close()
        return rows

    def execute_stored_procedure(self, procedure_name, params=None):
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(f"{{CALL {procedure_name}}}", params)
            else:
                cursor.execute(f"{{CALL {procedure_name}}}")
            rows = cursor.fetchall()
            resultset=[];
            if cursor.nextset():
                resultset.append(rows)
                resultset.append(cursor.fetchall())
            
        except Exception as error:
            print("Exception: ",error)
        finally:
            cursor.close()
        return rows

# Example usage:
if __name__ == "__main__":
    with DatabaseUtility() as db_utility:
        query_result = db_utility.execute_query("SELECT * FROM your_table")
        print(query_result)
