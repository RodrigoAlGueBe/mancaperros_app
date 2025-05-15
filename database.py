import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import urllib.parse

mode_prod = True

if mode_prod:
    # --------------------------- REMOTE CONNECTION ----------------------------
    # RAILWAY
    #db_url = os.getenv("DATABASE_URL")
    URL_DATABASE = "mysql+pymysql://root:VCNvQsaYzvYGEfkvesRyleOBVuhcAQOB@yamanote.proxy.rlwy.net:19041/railway"

    engine = create_engine(URL_DATABASE)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base = declarative_base()
    # --------------------------------------------------------------------------
    # # --------------------------- REMOTE CONNECTION ----------------------------
    # # AZURE
    # DB_USER = urllib.parse.quote_plus('erynfitadmin') # @erynfit')
    # DB_PASSWORD = urllib.parse.quote_plus('sgJW3a$@HfRmCx6')
    # DB_HOST = 'erynfit.mysql.database.azure.com'
    # DB_NAME = 'erynfit'
    # DB_PORT = '3306'

    # URL_DATABASE = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?ssl_ca=/etc/ssl/certs/ca-certificates.crt'

    # engine = create_engine(URL_DATABASE)

    # SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Base = declarative_base()
    # # --------------------------------------------------------------------------

else:
    # --------------------------- LOCAL CONNECTION ----------------------------
    SQLALCHEMY_DATABASE_URL = "sqlite:///./mancaperros_app.db"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base = declarative_base()
    # -------------------------------------------------------------------------