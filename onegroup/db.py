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
        self.init()
        self._db.row_factory = sqlite3.Row

    def init(self):
        #Tables
        self._db.execute('create table IF NOT EXISTS users (ID INTEGER PRIMARY KEY NOT NULL, Name text, Email text, Password text, Auth_Type text, Account_Type text, Keys text, Key_Distributed INTEGER, Grp INTEGER, Expiry text, Node INTEGER)')
        self._db.execute('create table IF NOT EXISTS groups (ID INTEGER PRIMARY KEY NOT NULL, Name text, Internal text, External text, Used_Octets text, Rule INTEGER, Node INTEGER)')
        self._db.execute('create table IF NOT EXISTS codes (Code text PRIMARY KEY NOT NULL, Name text, Purpose text, Used INTEGER)')
        self._db.execute('create table IF NOT EXISTS notifications (ID INTEGER PRIMARY KEY NOT NULL, User text, Request text)')
        self._db.execute('create table IF NOT EXISTS firewall (ID INTEGER PRIMARY KEY NOT NULL, Rule text, Policy INTEGER)')
        self._db.execute('create table IF NOT EXISTS nodes (ID INTEGER PRIMARY KEY NOT NULL, Name text, Address text)')

    def insert(self, table, row):
        keys = sorted(row.keys())
        values = [row[k] for k in keys]
        q = 'INSERT INTO {} ({}) VALUES ({})'.format(table,", ".join(keys),", ".join('?' for i in range(len(values))))
        self._db.execute(q,values)
        self._db.commit()

    def retrieve(self, table, keypairs = None):
        if keypairs != None:
            query = 'where'
            keys = sorted(keypairs.keys())
            values = tuple([keypairs[k] for k in keys])
            for key in keys:
                query += " {} = ? AND".format(key)

            query = query[:-4]
            cursor = self._db.execute('select * from {} {}'.format(table,query),values)
        else:
            cursor = self._db.execute('select * from {}'.format(table))
        
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
            if k != ID[0]:
                if isinstance(row[k],str):
                    setStr += '{} = "{}", '.format(k, row[k])
                else:
                    setStr += '{} = {}, '.format(k, row[k])

        #Remove trailing comma and space
        setStr = setStr[:(len(setStr)-2)]
 
        #Create Query
        q = 'update {} set {} where {} = ?'.format(table,setStr,ID[0])  
            
        #execute
        self._db.execute(q, (ID[1],) )
        self._db.commit()

    def delete(self, table, keypairs = None):
        query = '' 
        if keypairs:
            query = ' where'
            for key in keypairs:
                query += " {} = {} AND".format(key, keypairs[key])

            query = query[:-4]

        self._db.execute('delete from {}{}'.format(table, query))
        self._db.commit()

    def runSQL(self, sql):
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
