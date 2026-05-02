import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

def connectSQL():
    print("connecting to SQL...")

    load_dotenv()

    HOST_NAME = os.getenv("LOCAL_HOST_NAME")
    USER_NAME = os.getenv("LOCAL_USER_NAME")
    DB_PASSWORD = os.getenv("LOCAL_DB_PASSWORD")
    DB_DATABASE = os.getenv("LOCAL_DB_DATABASE")

    print("HOST_NAME:", HOST_NAME)
    print("USER_NAME:", USER_NAME)
    print("DB_PASSWORD:", DB_PASSWORD)
    print("DB_DATABASE:", DB_DATABASE)

    try:
        mydb = mysql.connector.connect(
            host=HOST_NAME,
            user=USER_NAME,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )

        if mydb.is_connected():
            print("Connection to MySQL successful!")
            return True, mydb

        print("MySQL connect returned object, but not connected.")
        return False, None

    except Error as err:
        return False, None
