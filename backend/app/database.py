import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def test_connection():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT version();")
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result[0]