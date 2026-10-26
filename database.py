
import sqlite3
import pandas as pd

DB_NAME = "air_quality.db"


def initialize_database():
    """Create the database table if it does not exist."""
    with sqlite3.connect(DB_NAME) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                city TEXT,
                european_aqi REAL,
                pm2_5 REAL,
                pm10 REAL,
                nitrogen_dioxide REAL,
                ozone REAL,
                carbon_monoxide REAL
            )
        """)


def save_readings(frame):
    """Save air-quality records from a Pandas DataFrame."""
    if frame is None or frame.empty:
        return

    columns = [
        "timestamp", "city", "european_aqi",
        "pm2_5", "pm10", "nitrogen_dioxide",
        "ozone", "carbon_monoxide"
    ]

    data = frame.reindex(columns=columns)

    with sqlite3.connect(DB_NAME) as connection:
        data.to_sql(
            "readings",
            connection,
            if_exists="append",
            index=False
        )


def load_all_readings(limit=500):
    """Load the most recent saved records."""
    initialize_database()

    with sqlite3.connect(DB_NAME) as connection:
        return pd.read_sql_query(
            "SELECT * FROM readings ORDER BY id DESC LIMIT ?",
            connection,
            params=(limit,)
        )
