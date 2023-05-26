import mysql.connector as mysql

class ConnectionError(Exception): ...

class MySQLHandler:
    def __init__(self, conn: mysql.MySQLConnection):
        self.conn   = conn
        self.cursor = conn.cursor()

    def execute(self, query, params = tuple(), rows = None, multi = False):
        self.cursor.execute(query, params, multi)
        
        if rows is None:
            return self.cursor.fetchall()
        else:
            return self.cursor.fetchmany(rows)
    
    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def columnNames(self):
        return self.cursor.column_names
    
    def close(self):
        self.cursor.close()
        self.conn.close()

class MySQL:
    def __init__(self, *args, **kwargs):
        self.conn      = mysql.connect(*args, **kwargs)
        self.__handler = None

        if not self.conn.is_connected():
            raise ConnectionError("Couldn't connect to database")
        
    def __enter__(self):
        self.__handler = MySQLHandler(self.conn)
        return self.__handler
    
    def __exit__(self, type, value, traceback):
        self.__handler.close()
        self.__handler = None