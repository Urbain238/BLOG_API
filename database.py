from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+pymysql://avnadmin:AVNS_1bEC-OGyJtQnF6sG6ep@mysql-181aa1f2-facsciences-c2d9.i.aivencloud.com:18684/defaultdb?ssl-mode=REQUIRED"

engine = create_engine(DATABASE_URL)

sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
