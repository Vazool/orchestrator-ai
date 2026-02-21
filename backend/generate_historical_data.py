import csv
import random

event_types = ["flight_disruption", "weather_delay", "airport_closure"]
location_types = ["airport", "city", "country"]
policy_types = ["standard", "gold", "platinum"] 
purposes = ["business", "leisure"]

rows = []

for _ in range(1200): 
    severity = random.randint(1, 5)
    event_type = random.choice(event_types)
    location_type = random.choice(location_types)
    days_before_travel = random.randint(0, 10)
    # Map to numeric: 0=Standard, 1=Gold, 2=Platinum
    policy_type_num = random.choice([0, 1, 2]) 
    # Map to numeric: 0=Leisure, 1=Business
    purpose_num = random.choice([0, 1])        

    # ML Logic: High severity + Business + Airport = High Disruption Risk
    if severity >= 4 and purpose_num == 1 and location_type == "airport":
        disruption = random.choices([0, 1], weights=[0.1, 0.9])[0]
    elif severity <= 2:
        disruption = random.choices([0, 1], weights=[0.95, 0.05])[0]
    else:
        disruption = random.choices([0, 1], weights=[0.5, 0.5])[0]

    rows.append([severity, event_type, location_type, days_before_travel, policy_type_num, purpose_num, disruption])

with open("historical_events.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["severity", "event_type", "location_type", "days_before_travel", "policy_type", "travel_purpose", "disruption"])
    writer.writerows(rows)

print("SUCCESS: historical_events.csv created.")
