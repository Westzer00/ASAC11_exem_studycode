import os

import psycopg
from fastapi import FastAPI

app = FastAPI()
DB_URL = os.environ["DATABASE_URL"]


@app.get("/")
def home():
    return {"message": "FastAPI 실행 중"}


@app.get("/db")
def db_test():
    with psycopg.connect(DB_URL) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS visits (
                id SERIAL PRIMARY KEY
            )
        """)
        conn.execute("INSERT INTO visits DEFAULT VALUES")

        count = conn.execute(
            "SELECT COUNT(*) FROM visits"
        ).fetchone()[0]

    return {
        "database": "connected",
        "visits": count
    }