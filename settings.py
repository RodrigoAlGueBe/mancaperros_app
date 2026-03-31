import os
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env
load_dotenv()

# ---------------------- VARIABLES GENERALES ----------------------
APP_NAME = "Mancaperros App"
VERSION = "1.0.0"

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

if all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
    DATABASE_URL = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
else:
    raise RuntimeError("DATABASE_URL not properly defined")
# -----------------------------------------------------------------

# ---------------------- VARIABLES DE LA APP ----------------------
ROUTINE_GROUP_ORDER_DEFAULT = '["chest", "back", "shoulders", "legs"]'
# -----------------------------------------------------------------