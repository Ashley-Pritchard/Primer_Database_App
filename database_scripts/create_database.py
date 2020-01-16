#ended up creating the database with django - not required 

import mysql.connector

db = mysql.connector.connect(
	host = 'localhost',
	user = 'ashley',
	passwd = 'primer_database',
	use_pure = True,
)

mycursor = db.cursor()

mycursor.execute('CREATE DATABASE primer_database')
