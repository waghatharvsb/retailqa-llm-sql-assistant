import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import DBAPIError

load_dotenv()

url = URL.create(
    "mysql+pymysql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", 3306)),
    database=os.getenv("DB_NAME"),
)
engine = create_engine(url)

with engine.connect() as conn:
    print("t_shirts rows :", conn.execute(text("SELECT COUNT(*) FROM t_shirts")).scalar())
    print("discounts rows:", conn.execute(text("SELECT COUNT(*) FROM discounts")).scalar())
    print("sample        :", conn.execute(text("SELECT brand, color, size, price, stock_quantity FROM t_shirts LIMIT 3")).fetchall())
    try:
        conn.execute(text("DELETE FROM t_shirts WHERE 1=0"))
        print("WARNING: DELETE was allowed, fix the qa_app grants!")
    except DBAPIError as e:
        print("DELETE denied (good):", str(e.orig)[:80])
