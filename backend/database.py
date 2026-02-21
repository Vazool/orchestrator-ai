import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# This builds an absolute path that Windows cannot misinterpret
basedir = os.path.dirname(os.path.abspath(__file__)) # The 'backend' folder
rootdir = os.path.dirname(basedir)                    # The 'Advanced-Lab-AI' folder
env_path = os.path.join(rootdir, ".env")

# explicitly tell it where the file is
load_dotenv(dotenv_path=env_path)

# DEBUG - Leave these in for one more run
print(f"DEBUG: Looking for file at: {env_path}")
print(f"DEBUG: Found file? {os.path.exists(env_path)}")
print(f"DEBUG: DB_PORT check: {os.getenv('DB_PORT')}")

# Add default fallbacks so the code doesn't crash if it still sees 'None'
db_user = os.getenv('DB_USER', 'root')
db_pass = os.getenv('DB_PASSWORD', 'root')
db_host = os.getenv('DB_HOST', '127.0.0.1')
db_port = os.getenv('DB_PORT', '3306') # Fallback to 3306
db_name = os.getenv('DB_NAME', 'europ_assistance_db')

DB_URL = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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