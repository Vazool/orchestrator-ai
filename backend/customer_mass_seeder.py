import random
from datetime import datetime, timedelta
from sqlalchemy import text
from database import SessionLocal

def seed_portfolio():
    db = SessionLocal()
    try:
        print("Starting 1000-record mass-seed...")
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        db.execute(text("TRUNCATE TABLE Travel;"))
        db.execute(text("TRUNCATE TABLE PolicyCoverage;"))
        db.execute(text("TRUNCATE TABLE Customers;"))
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

        for i in range(1, 1001):
            # Randomized Opt-in for GDPR demo
            optin = 1 if random.random() < 0.8 else 0
            
            # Match Step 1 Schema
            db.execute(text("""
                INSERT INTO Customers (forename, surname, email, optin, preferred_language, country, channel_type) 
                VALUES (:f, :s, :e, :o, 'en', 'UK', 'push')
            """), {"f": f"User{i}", "s": "Test", "e": f"user{i}@example.com", "o": optin})
            
            cust_id = db.execute(text("SELECT LAST_INSERT_ID()")).scalar()
            
            # Policy Logic
            p_type = 'platinum_all' if i <= 100 else random.choice(['flight_delay', 'weather_warning', 'basic_travel'])
            db.execute(text("INSERT INTO PolicyCoverage (customer_id, policy_type) VALUES (:cid, :pt)"), 
                       {"cid": cust_id, "pt": p_type})

            # Travel Logic Clusters
            if i <= 200: 
                arr, dest = 'CDG', 'FR-75' # Paris
            elif i <= 400: 
                arr, dest = 'MRS', 'FR-13' # Marseille
            elif i <= 600: 
                arr, dest = 'NCE', 'FR-06' # Nice
            else:
                arr, dest = 'LYS', 'FR-69' # Lyon

            db.execute(text("""
                INSERT INTO Travel (customer_id, arrival_airport, destination_region, start_date, end_date)
                VALUES (:cid, :arr, :dest, '2026-02-12', '2026-02-20')
            """), {"cid": cust_id, "arr": arr, "dest": dest})

        db.commit()
        print("SUCCESS: 1,000 records seeded. No more whack-a-mole.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_portfolio()