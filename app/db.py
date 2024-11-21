import os

from dotenv import load_dotenv
from sqlalchemy import JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()  # Meaningless in prod
db_url = os.getenv("DATABASE_URL") or ""  # Just to ensure str type
db_url = db_url.replace("postgres://", "postgresql://")  # For SQLAlchemy

engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base(type_annotation_map={dict: JSON})
