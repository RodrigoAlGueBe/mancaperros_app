from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --------------------------- REMOTE CONNECTION ----------------------------
DB_USER = 'erynfitadmin@erynfit'
DB_PASSWORD = 'sgJW3a$@HfRmCx6'
DB_HOST = 'erynfit.mysql.database.azure.com'
DB_NAME = 'erynfit'
DB_PORT = '3306'

URL_DATABASE = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?ssl_ca=/etc/ssl/certs/ca-certificates.crt'

engine = create_engine(URL_DATABASE)

sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
# --------------------------------------------------------------------------


# # --------------------------- LOCAL CONNECTION ----------------------------
# SQLALCHEMY_DATABASE_URL = "sqlite:///./mancaperros_app.db"

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()
# # -------------------------------------------------------------------------