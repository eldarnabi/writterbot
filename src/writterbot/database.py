from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = 'postgresql://eldar_the_admin:yaqDqW9yv2IbOAkXatZV4cvNJKWZ0BQz@dpg-ch9e3jrhp8u5mt973vj0-a.oregon-postgres.render.com/basement_07xg'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
base = declarative_base()
