import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. Load the secrets from your .env file
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")

if not all([DB_USER, DB_HOST, DB_NAME]):
    raise ValueError("CRITICAL: Missing Database environment variables. Check your .env file!")

# 2. Create the Connection String
# This tells Python: "Use the pymysql driver to talk to MySQL at this address"
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 3. Create the Engine and Session
# The 'engine' is the actual connection; the 'SessionLocal' is a factory for database conversations
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. The "Dependency"
# This helper function will be used by FastAPI to give each request its own database connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()