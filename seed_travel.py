import pandas as pd
from sqlalchemy import create_engine
import random

# Use your actual DB password here
engine = create_engine("mysql+pymysql://root:Orch3strator!@localhost/europ_assistance_db")

# 1. Fetch the 200 current customers (IDs 4 to 203)
cust_ids = pd.read_sql("SELECT customer_id FROM Customers", con=engine)['customer_id'].tolist()

# 2. Logic for UK -> France itineraries
uk_airports = ['LHR', 'LGW', 'LCY', 'MAN']
fr_airports = ['CDG', 'NCE', 'LYS', 'MRS']
today = pd.Timestamp.now().date()

trips = []
for cid in cust_ids:
    trips.append({
        "customer_id": cid,
        "start_date": today,
        "end_date": today + pd.Timedelta(days=7),
        "flight_number": f"EA{random.randint(100, 999)}",
        "departure_airport": random.choice(uk_airports),
        "arrival_airport": random.choice(fr_airports),
        "trip_status": "Planned" # Matches your DB constraint
    })

# 3. Inject into the travel table
pd.DataFrame(trips).to_sql('travel', con=engine, if_exists='append', index=False)
print(f"Success! Created {len(trips)} trips for your synthetic travelers.")