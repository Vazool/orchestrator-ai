from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import json

# Your custom connection logic
from database import engine, SessionLocal, get_db

import os
from openai import OpenAI

# Initialize the OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# See .env for the production toggle ("True" or "False")
IS_PROD = os.getenv("PRODUCTION_MODE", "False").lower() == "true"

def generate_ai_message(ctx: dict) -> str:
    """Uses GPT-4o-mini to write localized, empathetic support messages."""
    
    # Contextual instruction for the birthday logic
    birthday_instruction = (
        "This is a BIRTHDAY TRIP. Mention the celebration warmly and "
        "reassure them that we are here to protect their special plans." 
        if ctx['is_birthday_trip'] else "Standard professional support tone."
    )

    prompt = f"""
    You are a luxury travel concierge for Europ Assistance. 
    Write a supportive alert for:
    - Customer: {ctx['forename']}
    - Location: {ctx['destination']}
    - Event: {ctx['event_type']} (Severity {ctx['severity']}/5)
    - Policy: {ctx['policy_type']}
    - Language: {ctx['language']}

    Instruction: {birthday_instruction}
    Requirement: Max 50 words. If Language is not English, write the WHOLE message in that language.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an empathetic travel support agent."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Fallback to a safe default if the API hits a snag
        return f"Safety Alert: {ctx['event_type']} detected near {ctx['destination']}. Please stay safe."

app = FastAPI()

# Enable CORS for CJ's React App
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,  # Add this if you use cookies or auth
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/simulate-event")
def simulate_event(payload: dict, db: Session = Depends(get_db)):
    # 1. Record the Event
    event_sql = text("""
        INSERT INTO events (event_type, location_type, location_code, event_date, severity_level, source)
        VALUES (:et, :lt, :lc, :ed, :sl, :src)
    """)
    result = db.execute(event_sql, {
        "et": payload['event_type'], "lt": payload['location_type'],
        "lc": payload['location_code'], "ed": payload['event_date'],
        "sl": payload['severity_level'], "src": payload['source']
    })
    event_id = result.lastrowid

    # Initialize narrative counters
    TOTAL_PORTFOLIO = 1000
    counts = {
        "eligible": 0, 
        "goodwill": 0, 
        "no_consent": 0, 
        "already_contacted": 0
    }

    IS_PROD = False

    # 2. Updated Matching Logic (Now with Birthday Overlap Detection)
    matching_sql = text("""
        WITH RECURSIVE LocationHierarchy AS (
            SELECT location_id, code FROM locations WHERE code = :loc
            UNION ALL
            SELECT l.location_id, l.code
            FROM locations l
            INNER JOIN LocationHierarchy lh ON l.parent_location_id = lh.location_id
        )
        SELECT 
            t.travel_id, t.customer_id, t.final_destination,
            c.forename, c.optin, c.preferred_language, pc.policy_type,
            CASE 
                WHEN DATE_FORMAT(c.dob, '%m-%d') BETWEEN DATE_FORMAT(t.start_date, '%m-%d') AND DATE_FORMAT(t.end_date, '%m-%d')
                THEN 1 ELSE 0 
            END as is_birthday_trip
        FROM travel t
        JOIN customers c ON t.customer_id = c.customer_id
        JOIN policies pc ON c.customer_id = pc.customer_id  -- FIXED: Changed table from policycoverage to policies
        

        WHERE :event_date BETWEEN t.start_date AND t.end_date
        AND (
            t.arrival_airport = :loc OR 
            t.destination_region = :loc
        )
    """)
    
    impacted = db.execute(matching_sql, {
        "event_date": payload['event_date'],
        "loc": payload['location_code']
    }).fetchall()

    actual_impacted_count = len(impacted)  # Capture the true count before any safety slicing

    ai_call_count = 0  # We'll use this to track real API calls

    # 3. Decision Engine Logic - Now looping through EVERYTHING
    for index, traveler in enumerate(impacted):
        
        print(f"CRITICAL DEBUG: Traveler {index} | Count is {ai_call_count} | Condition: {ai_call_count < 10}")

        # GATE 1: PRIVACY (Consent Check)
        # Using != 1 catches 0, None, or False
        is_opted_in = int(traveler.optin) if traveler.optin is not None else 0

        if is_opted_in == 0:
            decision, reason = "no_action", "no_consent"
            counts["no_consent"] += 1
            msg = None
            print(f">>> PRIVACY BLOCK: {traveler.forename} (Value: {traveler.optin})")

        else:
            # GATE 2: DEDUPLICATION (State-Awareness Check) - removed AND e.event_type = :et
            
            dedup_sql = text("""
                SELECT COUNT(*) FROM decisions d
                JOIN events e ON d.event_id = e.event_id
                WHERE d.travel_id = :tid 
                    AND e.location_code = :loc 
                    AND d.decision_type != 'no_action'
                    AND e.event_date >= DATE_SUB(:ed, INTERVAL 7 DAY)
                    AND d.event_id != :current_eid
                """)
          
            is_dup = db.execute(dedup_sql, {
                "tid": traveler.travel_id, 
                "loc": payload['location_code'], 
                "ed": payload['event_date'],
                "current_eid": event_id
            }).scalar()

            if is_dup > 0:
                decision, reason = "no_action", "already_contacted"
                counts["already_contacted"] += 1
                msg = None
            
            # GATE 3: POLICY ELIGIBILITY & GATE 4: GOODWILL
            else:
                if traveler.policy_type == 'platinum_all' or traveler.policy_type == payload['event_type']:
                    decision, reason = "notify", "eligible"
                    counts["eligible"] += 1
                else:
                    decision, reason = "notify_safety_only", "goodwill_alert"
                    counts["goodwill"] += 1             
                
                # EMERGENCY EXIT: FORCE REAL AI
                ai_context = {
                    "forename": traveler.forename,
                    "destination": traveler.final_destination,
                    "event_type": payload['event_type'],
                    "severity": payload['severity_level'],
                    "policy_type": traveler.policy_type,
                    "is_birthday_trip": bool(traveler.is_birthday_trip),
                    "language": traveler.preferred_language
                }
                
                # Directly call the AI writer
                msg = generate_ai_message(ai_context)

                # Database Inserts
        dec_res = db.execute(text("""
            INSERT INTO decisions (event_id, travel_id, decision_type, reason_code)
            VALUES (:eid, :tid, :dt, :rc)
        """), {"eid": event_id, "tid": traveler.travel_id, "dt": decision, "rc": reason})
                
        if msg:  # Only create an action if there's a message to send    
            db.execute(text("""
                INSERT INTO actions (decision_id, channel_type, action_status, message)
                VALUES (:did, 'email', 'queued', :msg)
            """), {"did": dec_res.lastrowid, "msg": msg})                

    db.commit()

    # THE RECONCILIATION SUMMARY
    print(f"--- RESULTS FOR {payload['location_code']} ---")
    print(f"Total Found: {len(impacted)}")
    print(f"Privacy Blocks: {counts['no_consent']}")
    print(f"Deduplicated: {counts['already_contacted']}")
    print(f"AI Calls Made: {counts['eligible'] + counts['goodwill']}")

    return {
        "event_id": event_id,
        "total_records": TOTAL_PORTFOLIO,              
        "customers_evaluated": actual_impacted_count,
        "notifications_created": counts["eligible"] + counts["goodwill"],
        "customers_not_impacted": TOTAL_PORTFOLIO - actual_impacted_count,          

        # Use 'detailed_breakdown' here so it matches the /dashboard endpoint
        "detailed_breakdown": [
            {"category": "Eligible (Full Advice)", "count": counts["eligible"]},
            {"category": "Partial Cover (Goodwill)", "count": counts["goodwill"]},
            {"category": "No Consent (Privacy Block)", "count": counts["no_consent"]},
            {"category": "Already Contacted (Deduplicated)", "count": counts["already_contacted"]},
            {"category": "No Coverage", "count": 0}
        ]
    }

@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    # Returns latest notifications for CJ's NotificationScreen
    query = text("SELECT action_id as id, message, created_at as time FROM actions ORDER BY created_at DESC LIMIT 50")
    results = db.execute(query).fetchall()
    return [dict(r._mapping) for r in results]

@app.get("/dashboard")
def get_dashboard(event_id: int, db: Session = Depends(get_db)):
    query = text("""
        SELECT reason_code, COUNT(*) as count
        FROM decisions WHERE event_id = :eid
        GROUP BY reason_code
    """)
    results = db.execute(query, {"eid": event_id}).fetchall()
    breakdown = {r.reason_code: r.count for r in results}
    
    # This list now maps 1:1 with your Mermaid table categories
    return {
        "event_id": event_id,
        "detailed_breakdown": [
            {"category": "Eligible (Full Advice)", "count": breakdown.get('eligible', 0)},
            {"category": "Partial Cover (Goodwill)", "count": breakdown.get('goodwill_alert', 0)},
            {"category": "No Consent (Privacy Block)", "count": breakdown.get('no_consent', 0)},
            {"category": "Already Contacted (Deduplicated)", "count": breakdown.get('already_contacted', 0)},
            {"category": "No Coverage", "count": breakdown.get('no_coverage', 0)}
        ]
    }
