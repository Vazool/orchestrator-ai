import os
import pymysql
from dotenv import load_dotenv
from datetime import date
from privacy_vault import demo_vault # Import your new vault

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "europ_assistance_db"),
    "cursorclass": pymysql.cursors.DictCursor
}

def get_birthday_customers():
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT customer_id, forename, surname, dob, preferred_language 
                FROM customers 
                WHERE MONTH(dob) = MONTH(CURDATE()) AND DAY(dob) = DAY(CURDATE())
            """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        connection.close()

if __name__ == "__main__":
    today = date.today()
    targets = get_birthday_customers()
    print(f"--- BRUSSELS PROTOCOL: PRIVACY SCAN FOR {today} ---")
    
    for t in targets:
        # Stage 1: Mask the PII locally
        masked_name = demo_vault.mask_customer_data(t['forename'])
        
        print(f"Real Name: {t['forename']} {t['surname']}")
        print(f"AI Sees:   {masked_name} (ID: {t['customer_id']})")
        print(f"Language:  {t['preferred_language']}")
        print("-" * 30)
    
    print(f"\nVault Status: {len(demo_vault.map)} identities pseudonymized.")