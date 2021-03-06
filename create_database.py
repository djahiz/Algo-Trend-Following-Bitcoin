import sqlite3
from settings import *

db = sqlite3.connect(DB_NAME)

cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS data_order(
     ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
     LAST_TIMESTAMP INTEGER,
     ORDRE TEXT,
     WAY TEXT,
     PRICE REAL,
     GAIN REAL,
     COST REAL,
     FEE REAL,
     VOLUME REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS data_btc(
     ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
     LAST_TIMESTAMP INTEGER,
     OPEN REAL,
     HIGH REAL,
     LOW REAL,
     CLOSE REAL,
     MEAN_OPEN REAL,
     MEAN_CLOSE REAL,
     VOL_OPEN REAL,
     VOL_CLOSE REAL,
     PRICE_UP_OPEN REAL,
     PRICE_DOWN_OPEN REAL,
     PRICE_UP_CLOSE REAL,
     PRICE_DOWN_CLOSE REAL,
     VOLUME REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bot_state(
     ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
     LAST_TIMESTAMP INTEGER,
     LONG BOOLEAN,
     SHORT BOOLEAN,
     CLOSE_CONFIRMATION INTEGER,
     OPEN_PRICE REAL,
     CLOSE_PRICE REAL,
     EXTREME_VALUE REAL,
     BARRIER BOOLEAN,
     WAIT_CLOSE_LONG BOOLEAN,
     WAIT_CLOSE_SHORT BOOLEAN
)
""")

db.commit()

db.close()