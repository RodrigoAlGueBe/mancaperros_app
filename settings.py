import os
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env
load_dotenv()

# ---------------------- VARIABLES GENERALES ----------------------
APP_NAME = "Mancaperros App"
VERSION = "1.0.0"

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
# -----------------------------------------------------------------

# ---------------------- VARIABLES DE LA APP ----------------------
ROUTINE_GROUP_ORDER_DEFAULT = '["chest", "back", "shoulders", "legs"]'
# -----------------------------------------------------------------
