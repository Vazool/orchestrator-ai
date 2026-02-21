import random
from faker import Faker
from sqlalchemy import text
from database import SessionLocal
from datetime import datetime, timedelta

fake = Faker(['en_GB', 'fr_FR'])

destinations = [
    ('Cannes', 'NCE', 'Alpes-Maritimes'), ('Antibes', 'NCE', 'Alpes-Maritimes'), 
    ('Grasse', 'NCE', 'Alpes-Maritimes'), ('Cagnes-sur-Mer', 'NCE', 'Alpes-Maritimes'), 
    ('Nice', 'NCE', 'Alpes-Maritimes'), ('Villeurbanne', 'LYS', 'Rhône'), 
    ('Vénissieux', 'LYS', 'Rhône'), ('Vaulx-en-Velin', 'LYS', 'Rhône'), 
    ('Caluire-et-Cuire', 'LYS', 'Rhône'), ('Lyon', 'LYS', 'Rhône'),
    ('Aix-en-Provence', 'MRS', 'Bouches-du-Rhône'), ('Arles', 'MRS', 'Bouches-du-Rhône'), 
    ('Martigues', 'MRS', 'Bouches-du-Rhône'), ('Salon-de-Provence', 'MRS', 'Bouches-du-Rhône'), 
    ('Marseille', 'MRS', 'Bouches-du-Rhône'), ('Paris', 'CDG', 'Paris')
]

def seed_everything():
    db = SessionLocal()
    try:
        print("Cleaning up old data...")
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        db.execute(text("TRUNCATE TABLE travel;"))
        db.execute(text("TRUNCATE TABLE policies;"))
        db.execute(text("TRUNCATE TABLE customers;"))
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

        print("Generating 1000 high-fidelity records with 5% birthday matches...")
        for i in range(1, 1001):
            # --- 1. TRAVEL DATA FIRST (to determine birthday logic) ---
            town, airport, region = random.choice(destinations)
            start_date = datetime(2026, 2, 10) + timedelta(days=random.randint(0, 5))
            end_date = start_date + timedelta(days=random.randint(3, 10))

            
            # --- 2. CUSTOMER DATA ---
            fn = fake.first_name()
            sn = fake.last_name()
            email = f"{fn[0].lower()}.{sn.lower()}@{fn.lower()}.com"
            
            # 1. New Language Logic
            pref_lang = random.choice(['English', 'French', 'German'])
            
            # 2. New Opt-in Logic (85% opt-in, 15% opt-out)
            user_optin = 1 if random.random() > 0.15 else 0

            # 5% chance of birthday falling during trip
            if random.random() < 0.05:
                delta_days = (end_date - start_date).days
                match_date = start_date + timedelta(days=random.randint(0, delta_days))
                birth_year = datetime.now().year - random.randint(18, 80)
                dob = match_date.replace(year=birth_year).date()
            else:
                dob = fake.date_of_birth(minimum_age=18, maximum_age=80)
            
            db.execute(
                text("""INSERT INTO customers (customer_id, forename, surname, email, dob, optin, preferred_language) 
                        VALUES (:id, :fn, :sn, :em, :dob, :opt, :lang)"""),
                {"id": i, "fn": fn, "sn": sn, "em": email, "dob": dob, "opt": user_optin, "lang": pref_lang}
            )
            
            # --- 3. POLICY DATA ---
            p_type = 'platinum_all' if random.random() > 0.3 else 'standard_cover'
            db.execute(
                text("INSERT INTO policies (customer_id, policy_type) VALUES (:cid, :pt)"),
                {"cid": i, "pt": p_type}  # Changed 'cid' to 'i' here
            )

            # --- 4. TRAVEL DATA INSERT ---
            db.execute(
                text("""INSERT INTO travel (customer_id, arrival_airport, destination_region, final_destination, start_date, end_date) 
                        VALUES (:cid, :air, :reg, :town, :sd, :ed)"""),
                {"cid": i, "air": airport, "reg": region, "town": town, "sd": start_date, "ed": end_date} # Changed 'cid' to 'i' here
            )

        db.commit()
        print("Success! Data loaded with birthday 'hooks' ready for the AI.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_everything()