from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from .config import settings
SQLALCHEMY_DATABASE_URL=f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine=create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal= sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base=declarative_base()

def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()
# manual postgresql connection retry loop
# while True:
#     try:
#         conn=psycopg2.connect(host='localhost',database='fastapi',user='postgres',password='fastapi@123',cursor_factory=RealDictCursor)
#         cursor=conn.cursor()
#         print("Database connection was successfull!")
#         break
#     except Exception as error:
#         print("connecting to database failed")
#         print("error:",error)
#         time.sleep(2)
my_posts=[{"title":"titile of post 1 ","id":1},
          {"title":"faourite food ","content":"i like pizza","id":2}]