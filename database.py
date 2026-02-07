import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

import urllib.parse

mode_prod = False

if mode_prod:
    # --------------------------- REMOTE CONNECTION ----------------------------
    # RAILWAY
    #db_url = os.getenv("DATABASE_URL")
    DB_USER = urllib.parse.quote_plus('root')
    DB_PASSWORD = urllib.parse.quote_plus('VCNvQsaYzvYGEfkvesRyleOBVuhcAQOB')
    DB_HOST = 'yamanote.proxy.rlwy.net'
    DB_NAME = 'railway'
    DB_PORT = '19041'

    URL_DATABASE = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    engine = create_engine(URL_DATABASE)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base = declarative_base()
    # --------------------------------------------------------------------------
    # # --------------------------- REMOTE CONNECTION ----------------------------
    # # AZURE DEPRECATED
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
    # SQLALCHEMY_DATABASE_URL = "sqlite:///./mancaperros_app.db"

    # engine = create_engine(
    #     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    # )

    # SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Base = declarative_base()
    load_dotenv()
    
    DATABASE_URL = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:"
        f"{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_NAME')}"
    )

    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    
    Base = declarative_base()
    # -------------------------------------------------------------------------