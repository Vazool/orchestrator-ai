import random
import string
from faker import Faker
from sqlalchemy import text
from database import SessionLocal
from datetime import datetime, timedelta

fake = Faker(['en_GB', 'fr_FR', 'nl_BE']) # Added Flemish support

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

hubs = ['MAD', 'LHR', 'CDG']

def generate_flight_no():
    """Generates a flight number like LHR7721"""
    letters = "".join(random.choices(string.ascii_uppercase, k=3))
    numbers = "".join(random.choices(string.digits, k=4))
    return f"{letters}{numbers}"

def seed_everything():
    db = SessionLocal()
    try:
        print("Cleaning up old data...")
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        db.execute(text("TRUNCATE TABLE travel;"))
        db.execute(text("TRUNCATE TABLE policies;"))
        db.execute(text("TRUNCATE TABLE customers;"))
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

        print("Generating 1000 high-fidelity records with new ML features...")
        for i in range(1, 1001):
            # --- 1. TRAVEL DATA PREP ---
            town, dest_airport, region = random.choice(destinations)
            start_date = datetime(2026, 2, 10) + timedelta(days=random.randint(0, 5))
            end_date = start_date + timedelta(days=random.randint(3, 10))
            
            # Flight Details
            dep_airport = random.choice([h for h in hubs if h != dest_airport])
            flight_no = generate_flight_no()
            
            # --- 2. CUSTOMER DATA ---
            fn = fake.first_name()
            sn = fake.last_name()
            email = f"{fn[0].lower()}.{sn.lower()}@{fn.lower()}.com"
            
            # Language Weights: 50% EN, 20% FR, 20% DE, 10% Flemish
            pref_lang = random.choices(
                ['English', 'French', 'German', 'Flemish'], 
                weights=[0.5, 0.2, 0.2, 0.1], k=1
            )[0]
            
            user_optin = 1 if random.random() > 0.15 else 0
            travel_purpose = random.choice(['leisure', 'business'])

            # Birthday Logic
            if random.random() < 0.05:
                delta_days = (end_date - start_date).days
                match_date = start_date + timedelta(days=random.randint(0, delta_days))
                dob = match_date.replace(year=datetime.now().year - random.randint(18, 80)).date()
            else:
                dob = fake.date_of_birth(minimum_age=18, maximum_age=80)
            
            db.execute(
                text("""INSERT INTO customers (customer_id, forename, surname, email, dob, optin, preferred_language, travel_purpose) 
                        VALUES (:id, :fn, :sn, :em, :dob, :opt, :lang, :tp)"""),
                {"id": i, "fn": fn, "sn": sn, "em": email, "dob": dob, "opt": user_optin, "lang": pref_lang, "tp": travel_purpose}
            )
            
            # --- 3. POLICY DATA (Standardized 0, 1, 2) ---
            # 30% Platinum (2), 30% Gold (1), 40% Standard (0)
            p_type = random.choices([0, 1, 2], weights=[0.4, 0.3, 0.3], k=1)[0]
            db.execute(
                text("INSERT INTO policies (customer_id, policy_type) VALUES (:cid, :pt)"),
                {"cid": i, "pt": p_type}
            )

            # --- 4. TRAVEL DATA INSERT (With Hubs & Flight Numbers) ---
            db.execute(
                text("""INSERT INTO travel (customer_id, arrival_airport, departure_airport, flight_number, destination_region, final_destination, start_date, end_date) 
                        VALUES (:cid, :air, :dep, :fno, :reg, :town, :sd, :ed)"""),
                {"cid": i, "air": dest_airport, "dep": dep_airport, "fno": flight_no, "reg": region, "town": town, "sd": start_date, "ed": end_date}
            )

        db.commit()
        print("Success! 1000 records seeded with localized languages and flight numbers.")
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_everything()