# Brenton Klassen
# 8/28/2014
# connect to Sql Server db

import pypyodbc
import atexit
import settings

connstr = settings.get('sqlconnstr')

print('Connecting to the db...')

conn = pypyodbc.connect(connstr)
cur = conn.cursor()

def closeConn():
    cur.close()
    conn.close()

atexit.register(closeConn)
