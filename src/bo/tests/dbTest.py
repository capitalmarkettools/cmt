#===============================================================================
# server_version.py - retrieve and display database server version
# this is old and can be removed. I will still keep it around just in
# case I want to play with MySQLdb
#===============================================================================

import MySQLdb

conn = MySQLdb.connect (host = "localhost", user = "root", 
                        passwd = "XXX", db = "Test1")
cursor = conn.cursor ()
cursor.execute ("SELECT VERSION()")
row = cursor.fetchone ()
print "server version:", row[0]
cursor.close ()
conn.close ()
