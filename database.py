from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

DATABASE_URL = "postgresql+psycopg2://recipe_user:recipe_pw@localhost:5432/recipe_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)
