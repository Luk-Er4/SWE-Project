import mysql.connector
from mysql.connector import Error

def connectSQL():
    print("connecting to SQL...")

    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="healthsys"
        )

        if mydb.is_connected():
            print("Connection to MySQL successful!")
            return True, mydb

    except Error as err:
        return f"Error connecting to MySQL: {err}"
