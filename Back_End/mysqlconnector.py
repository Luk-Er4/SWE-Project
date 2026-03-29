import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os


def connectSQL():
    print("connecting to SQL...")

    load_dotenv()

    HOST_NAME = os.getenv("AWS_DB_HOST")
    USER_NAME = os.getenv("AWS_DB_USER")
    DB_PASSWORD = os.getenv("AWS_DB_PW")
    DB_DATABASE = os.getenv("AWS_DB_NAME")

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

    except Error as err:
        return False, None
