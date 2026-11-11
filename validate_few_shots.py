import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from few_shots import few_shots

load_dotenv()
engine = create_engine(URL.create(
    "mysql+pymysql",
    username=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"), port=int(os.getenv("DB_PORT", 3306)),
    database=os.getenv("DB_NAME"),
))

with engine.connect() as conn:
    for i, ex in enumerate(few_shots, 1):
        try:
            rows = conn.execute(text(ex["SQLQuery"])).fetchall()
            print(f"{i:2}. OK    {rows[:2]}   <- {ex['Question'][:55]}")
        except Exception as e:
            print(f"{i:2}. ERROR {str(e)[:100]}   <- {ex['Question'][:55]}")
