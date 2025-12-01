# init_db.py
import os
from sqlalchemy import create_engine
from main import Base  # your declarative_base() from main.py

# Use the same DATABASE_URL as in server.py
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://bcfuser:bcfpass@db:5432/bcfdb",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

if __name__ == "__main__":
    print("Creating tables in bcfdb...")
    Base.metadata.create_all(engine)
    print("Done.")
