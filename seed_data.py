import pandas as pd
from sqlalchemy import create_engine
from faker import Faker
import random

fake = Faker()
# Update with your password!
engine = create_engine("mysql+pymysql://root:Orch3strator!@localhost/europ_assistance_db")

# 1. Generate 200 Customers mapped to your REAL columns
locations = ["CDG", "LHR", "JFK", "FRA", "DXB"]
languages = ["en", "fr", "es", "de"]

cust_list = []
for _ in range(200):
    cust_list.append({
        "forename": fake.first_name(),
        "surname": fake.last_name(),
        "email": fake.email(),
        "phone": fake.phone_number()[:20], # Truncate to fit VARCHAR(20)
        "current_location": random.choice(locations),
        "preferred_language": random.choice(languages),
        "optin": 1,
        "country": fake.country_code(),
        "channel_type": "email"
    })

df_cust = pd.DataFrame(cust_list)
df_cust.to_sql('Customers', con=engine, if_exists='append', index=False)

# 2. Link Policies to these new IDs
# We fetch the IDs we just created to ensure the Foreign Key matches
new_ids = pd.read_sql("SELECT customer_id FROM Customers ORDER BY customer_id DESC LIMIT 200", con=engine)

policy_types = ['medical', 'flight_disruption', 'luggage', 'platinum_all']
pol_list = [
    {"customer_id": row['customer_id'], "policy_type": random.choice(policy_types), "status": "active"}
    for _, row in new_ids.iterrows()
]

pd.DataFrame(pol_list).to_sql('PolicyCoverage', con=engine, if_exists='append', index=False)

print("Success! 200 Customers and Policies are live.")