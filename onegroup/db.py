"""
db.py V3 

Created, Written, Developed and Designed by
Sebastian Sherry

"""
import sqlite3

class Database:
    def __init__(self, **kwargs):
        self.filename = kwargs.get('filename')
        self._db = sqlite3.connect(self.filename)
        self.check_empty()
        self._db.row_factory = sqlite3.Row

    def check_empty(self):
        #Check if the database is empty. If not the exit
        cursor = self._db.execute("SELECT name from sqlite_master WHERE type='table';") 
        if len([x for x in cursor.fetchall()]) > 0:
            return
        
        #Tables
        self._db.execute('create table IF NOT EXISTS users (ID INTEGER PRIMARY KEY NOT NULL, Name text, Email text, Password text, Auth_Type text, Account_Type text, Keys text, Key_Distributed INTEGER)')

    def insert(self, table, row):
        keys = sorted(row.keys())
        values = [row[k] for k in keys]
        q = 'INSERT INTO {} ({}) VALUES ({})'.format(table,", ".join(keys),", ".join('?' for i in range(len(values))))
        self._db.execute(q,values)
        self._db.commit()

    def retrieve(self, table, key, val):
        cursor = self._db.execute('select * from {} where {} = ?'.format(table, key), (val,))
        
        rows = [dict(row) for row in cursor.fetchall()]
        if len(rows) == 0:
            return None
        elif len(rows) == 1:
            return rows[0]
        else:
            return rows
                
    def retrieveAll(self, table):
        cursor = self._db.execute('select * from {}'.format(table))
        
        rows = [dict(row) for row in cursor.fetchall()]
        return rows

    
    def update(self, table, row, ID):
        #Create set method
        setStr = ""
        for k in row:
            if k != 'ID':
                setStr += "{} = {}, ".format(k, row[k])

        #Remove trailing comma and space
        setStr = setStr[:(len(setStr)-2)]
        print(setStr) 
        #execute
        self._db.execute('update {} set {}  where ID = ?'.format(table,setStr),(ID,))
        self._db.commit()

    def delete(self, table, key, val):
        self._db.execute('delete from {} where {} = ?'.format(table, key),(val,))
        self._db.commit()

    def RunSQL(self, sql):
        #TODO SQL INJECTION TESTING
        self._db.execute(sql)
        self._db.commit()

    def close(self):
        self._db.close()
        del self.filename

    def __iter__(self):
        cursor = self._db.execute('select * from {}'.format(self._table))
        for row in cursor:
            yield dict(row)


if __name__ == "__main__":
    filen = "OneGroup.db"       #Database
    db = Database(filename = filen)
    users = db.retrieveAll("users")
    print(users)
    db.close()
