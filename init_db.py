import pymysql
import os

import urllib.parse
from dotenv import load_dotenv

# --------------------------- REMOTE CONNECTION ----------------------------
# DB_HOST = 'erynfit.mysql.database.azure.com'
# DB_USER = 'erynfitadmin@erynfit'
# DB_PASSWORD = 'sgJW3a$@HfRmCx6'
# DB_PORT = 3306
# DB_NAME = 'erynfit'

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME")

def create_database_if_not_exists():
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        ssl={'ca': '/etc/ssl/certs/ca-certificates.crt'} if os.getenv("DB_SSL") == "true" else None
    )

    with connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};")
        print(f"✔ Base de datos '{DB_NAME}' verificada o creada.")
    connection.close()
# --------------------------------------------------------------------------

if __name__ == "__main__":
    create_database_if_not_exists()