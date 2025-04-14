import pymysql

import urllib.parse

# --------------------------- REMOTE CONNECTION ----------------------------
DB_HOST = 'erynfit.mysql.database.azure.com'
DB_USER = 'erynfitadmin@erynfit'
DB_PASSWORD = 'sgJW3a$@HfRmCx6'
DB_PORT = 3306
DB_NAME = 'erynfit'

def create_database_if_not_exists():
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        ssl={'ca': '/etc/ssl/certs/ca-certificates.crt'}
    )

    with connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};")
        print(f"✔ Base de datos '{DB_NAME}' verificada o creada.")
    connection.close()

if __name__ == "__main__":
    create_database_if_not_exists()