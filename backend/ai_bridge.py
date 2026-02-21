import os
import pymysql
from dotenv import load_dotenv
from datetime import date

# This looks for the .env file in the current directory
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"), # No more hardcoding!
    "database": os.getenv("DB_NAME", "europ_assistance_db"),
    "cursorclass": pymysql.cursors.DictCursor
}

def get_birthday_customers():
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # The query you just proved works
            sql = "SELECT customer_id, forename, surname, dob FROM customers WHERE MONTH(dob) = MONTH(CURDATE()) AND DAY(dob) = DAY(CURDATE())"
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        connection.close()

if __name__ == "__main__":
    today = date.today()
    targets = get_birthday_customers()
    print(f"--- AI SCAN FOR {today} ---")
    print(f"Found {len(targets)} customers requiring personalized outreach.")
    for t in targets:
        print(f"Target: {t['forename']} {t['surname']} (DOB: {t['dob']})")