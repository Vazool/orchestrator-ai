import sys
import os
from sqlalchemy import text

# 1. Import your existing engine and SessionLocal from your own database.py
# This ensures we use your EXACT credentials and connection logic
from database import engine

def groom_for_demo():
    print("Connecting to MySQL via database.py config...")
    
    # We use a context manager to ensure the connection closes properly
    with engine.connect() as conn:
        print("Grooming NCE for Paris Demo...")

        # 1. Reset NCE travelers
        # Note: We reset the optin and birthday status for everyone arriving at NCE
        conn.execute(text("""
            UPDATE customers c
            JOIN travel t ON c.customer_id = t.customer_id
            SET c.optin = 1
            WHERE t.arrival_airport = 'NCE'
        """))

        # 2. Grab Customer IDs for all NCE travelers
        result = conn.execute(text("SELECT customer_id FROM travel WHERE arrival_airport = 'NCE'"))
        travelers = [row[0] for row in result.fetchall()]
        
        total_found = len(travelers)
        print(f"Found {total_found} travelers arriving at NCE.")

        if total_found < 30:
            print(f"Warning: Only found {total_found} travelers. Run unified_seeder.py first!")
            return

        # 3. Precise Grooming: 6 Opt-outs (First 6)
        opt_out_ids = travelers[:6]
        conn.execute(text("UPDATE customers SET optin = 0 WHERE customer_id IN :ids"), {"ids": opt_out_ids})

        # 4. Precise Grooming: 2 Birthdays (Next 2)
        # We set their DOB to Feb 12th to match your demo date '12/02/2026'
        birthday_ids = travelers[6:8]
        demo_date = "2026-02-12"
        conn.execute(text("""
            UPDATE customers 
            SET dob = :dob_match
            WHERE customer_id IN :ids
        """), {"dob_match": "1990-02-12", "ids": birthday_ids})

        # 5. Delete extras to leave exactly 30
        if total_found > 30:
            extra_ids = travelers[30:]
            # Delete from travel first (Foreign Key safety), then customers if you want to keep it clean
            conn.execute(text("DELETE FROM travel WHERE customer_id IN :ids"), {"ids": extra_ids})
            conn.execute(text("DELETE FROM policies WHERE customer_id IN :ids"), {"ids": extra_ids})
            conn.execute(text("DELETE FROM customers WHERE customer_id IN :ids"), {"ids": extra_ids})
            print(f"Removed {len(extra_ids)} extra records.")

        conn.commit()
        print("\nSuccess! NCE is groomed: 30 travelers, 6 opt-outs, 2 birthdays (IDs in positions 7 and 8).")

if __name__ == "__main__":
    groom_for_demo()