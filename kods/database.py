import sqlite3
import pandas as pd

DATABASE = "invoices.db"
EXCEL_FILE = "emissions.xlsx"

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        cursor.execute("""
                DROP TABLE invoices
                """)

        cursor.execute("""
                        DROP TABLE users
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
            fails TEXT
        )
        """)
        conn.commit()
    # import_emissions()


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
    # with sqlite3.connect(DATABASE) as conn:
    #     cursor = conn.cursor()
    #     cursor.execute("""
    #                     DROP TABLE IF EXISTS emissions
    #                     """)
    #
    #     cursor.execute("""
    #     CREATE TABLE IF NOT EXISTS emissions (
    #         type_id INTEGER PRIMARY KEY,
    #         type_name TEXT,
    #         type_decode_lv TEXT,
    #         units TEXT,
    #         value FLOAT
    #     )
    #     """)

        # mapped_df.to_sql('emissions', conn, if_exists='append', index=False)
        # conn.commit()


def save_to_db(data):
    print()
    print(data)
    print()
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.executemany("""
        INSERT INTO invoices (firma, datums, produkts, daudzums, cena, emisija, fails)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, data)
        conn.commit()

def fetch_from_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM invoices")
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