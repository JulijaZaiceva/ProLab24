import sqlite3
import pandas as pd

DATABASE = "invoices.db"
EXCEL_FILE = "emissions.xlsx"

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        cursor.execute("""
                DROP TABLE IF EXISTS invoices
                """)

        cursor.execute("""
                        DROP TABLE IF EXISTS users
                        """)

        cursor.execute("""
                        DROP TABLE IF EXISTS bundles
                        """)

        cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
                )
                """)



        cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firma TEXT NOT NULL,
            datums TEXT NOT NULL,
            produkts TEXT NOT NULL,
            daudzums TEXT,
            cena TEXT,
            emisija FLOAT,
            fails TEXT,
            bundle_id TEXT
        )
        """)

        cursor.execute("""
                CREATE TABLE IF NOT EXISTS bundles (
                    id TEXT PRIMARY KEY,
                    username TEXT,
                    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """)

        conn.commit()

def fetch_user_bundles(username):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                b.id AS bundle_id,
                b.timestamp AS bundle_timestamp,
                i.id AS invoice_id,
                i.firma,
                i.datums,
                i.produkts,
                i.daudzums,
                i.cena,
                i.emisija,
                i.fails
            FROM bundles b
            LEFT JOIN invoices i ON b.id = i.bundle_id
            WHERE b.username = ?
            ORDER BY b.timestamp ASC, i.id ASC
        """, (username,))

        rows = cursor.fetchall()
        bundles = {}

        for row in rows:
            bundle_id = row[0]
            bundle_timestamp = row[1]
            invoice_data = {
                "invoice_id": row[2],
                "firma": row[3],
                "datums": row[4],
                "produkts": row[5],
                "daudzums": row[6],
                "cena": row[7],
                "emisija": row[8],
                "fails": row[9]
            }

            if bundle_id not in bundles:
                bundles[bundle_id] = {
                    "bundle_id": bundle_id,
                    "timestamp": bundle_timestamp,
                    "invoices": []
                }
            if invoice_data["invoice_id"]:
                bundles[bundle_id]["invoices"].append(invoice_data)

        return list(bundles.values())

def create_bundle(id, username):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO bundles (id, username) VALUES (?, ?)",
                       (id, username))
        conn.commit()

def import_emissions():
    df = pd.read_excel(EXCEL_FILE, sheet_name=1)
    mapped_df = df.rename(columns={
        "Type_ID": "type_id",
        "Type_Name" : "type_name",
        "Type_Decode_LV" :"type_decode_lv",
        "Mērvienība": "units",
        "CO2 uz kg" : "value"
    })
    mapped_df = mapped_df[["type_id", "type_name","type_decode_lv","units","value"]]
    return mapped_df.to_dict(orient="records")

def save_to_db(data):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.executemany("""
        INSERT INTO invoices (firma, datums, produkts, daudzums, cena, emisija, fails, bundle_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        conn.commit()

def fetch_from_db(bundle_id):
    if not bundle_id:
        return []

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT firma, datums, produkts, daudzums, cena, emisija, fails FROM invoices where bundle_id = ?", (bundle_id,))
        return cursor.fetchall()

def save_user(username, hashed_password):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       (username, hashed_password, "COMPANY_USER"))
        conn.commit()

def find_user(username):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, password, role FROM users WHERE username = ?", (username,))
        return cursor.fetchone()