import joblib
import pandas as pd
import random

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

import json

# Your custom connection logic
from database import engine, SessionLocal, get_db

# GDPR Privacy Vault
from privacy_engine import demo_vault

import os
from openai import OpenAI

# --- Global Policy Configuration ---
POLICY_FEATURES = {
    0: {  # Basic
        "label": "Basic",
        "medical": "up to £2m",
        "repatriation": "Standard",
        "cancellation": "specified causes only",
        "concierge": "None",
        "disruption": "None"
    },
    1: {  # Standard
        "label": "Standard",
        "medical": "up to £5m",
        "repatriation": "Standard",
        "cancellation": "extended causes",
        "concierge": "24/7 helpline",
        "disruption": "None"
    },
    2: {  # Platinum
        "label": "Platinum",
        "medical": "unlimited / £10m+",
        "repatriation": "Priority + upgraded travel",
        "cancellation": "incl. discretionary cancel for work issues",
        "concierge": "dedicated case handler",
        "disruption": "proactive disruption alerts + auto-claims"
    }
}

# Initialize the OpenAI Client - OLD
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize the OpenAI Client
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

# See .env for the production toggle ("True" or "False")
IS_PROD = os.getenv("PRODUCTION_MODE", "False").lower() == "true"

def generate_ai_message(ctx: dict) -> str:
    """Uses GPT-4o-mini to write messages using tokens instead of real names."""
    
    # --- STAGE 1: MASKING (Brussels Protocol) ---
    # We swap the real name for a token like {{forename_1}}
    real_forename = ctx.get('forename', 'Traveler')
    masked_forename = demo_vault.mask_customer_data(real_forename)

    # 1. New Risk-Level Instruction
    risk_val = ctx.get('risk_score', 0)
    if risk_val >= 70:
        urgency_instruction = "This is a HIGH RISK situation. Use a proactive, protective, and urgent tone."
    elif risk_val >= 40:
        urgency_instruction = "This is a MODERATE RISK situation. Use a helpful, advisory, and vigilant tone."
    else:
        urgency_instruction = "Standard advisory tone."

    # 2. Dynamic Policy Fact Injection
    policy_facts = (
        f"The customer has {ctx['policy_label']} coverage. "
        f"Key benefits to mention if relevant: Medical cover {ctx['medical_limit']}, "
        f"Repatriation: {ctx['repatriation']}, Cancellation: {ctx['cancel_terms']}. "
        f"Concierge Access: {ctx['concierge_perk']}."
    )

    # 3. Platinum "Option Identification" Logic (The 'Brussels Scout' approach)
    platinum_instruction = ""
    if ctx.get('policy_type') == 2:
        platinum_instruction = (
            f"As a PLATINUM member, mention their 'Proactive Disruption Benefit' ({ctx['disruption_benefit']}). "
            f"Crucially, inform them that our team has already IDENTIFIED a potential alternative flight: "
            f"{ctx.get('flight_number')} departing from {ctx.get('dep_airport')} at {ctx.get('alt_time')}. "
            f"Clarify that this is an available option we have found for them, and they should "
            f"contact their dedicated case handler to discuss or finalize arrangements if they wish to proceed."
        )
    
    # 4. Birthday Logic
    birthday_instruction = (
        "This is a BIRTHDAY TRIP. Mention the celebration warmly and "
        "reassure them that we are here to protect their special plans." 
        if ctx.get('is_birthday_trip') else ""
    )

    # 5. Language Extraction
    target_lang = ctx.get('language', 'English')

    # UPDATED PROMPT: Notice we use masked_forename and a new Constraint
    prompt = f"""
    You are a luxury travel concierge for Europ Assistance. 
    Write a supportive alert in {target_lang} for:
    - Customer: {masked_forename}
    - Location: {ctx['destination']}
    - Event: {ctx['event_type']} (Severity {ctx['severity']}/5)
    - Calculated Disruption Risk: {risk_val}%
    
    Policy Context: {policy_facts}
    
    Tone Guidance: {urgency_instruction}
    {platinum_instruction}
    {birthday_instruction}

    Constraints: 
    1. Keep the message under 4 sentences. 
    2. Use the exact tag {masked_forename} to address the customer. 
    3. Do NOT invent a name or use generic greetings like 'Dear Customer'.
    4. Incorporate 1-2 specific policy facts.
    5. Output MUST be in {target_lang}.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": f"You are an empathetic support agent. Use the provided {{tags}} for names exactly as they appear."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        # --- STAGE 2: REHYDRATION ---
        # The AI returns text containing "{{forename_1}}"
        raw_content = response.choices[0].message.content.strip()
        
        # We swap it back to the real name locally
        final_message = demo_vault.rehydrate_message(raw_content)
        
        return final_message

    except Exception as e:
        print(f"AI Error: {e}")
        # Local fallback also uses the real name safely
        return f"Safety Alert: {ctx['event_type']} detected near {ctx['destination']}. {real_forename}, please contact your {ctx['policy_label']} support line."

app = FastAPI()

# ─── DB MIGRATION NOTE ────────────────────────────────────────────────────────
# Run these once against your database before starting the server:
#
#   ALTER TABLE actions ADD COLUMN is_read TINYINT(1) NOT NULL DEFAULT 0;
#
#   CREATE TABLE IF NOT EXISTS alert_feedback (
#       feedback_id  INT AUTO_INCREMENT PRIMARY KEY,
#       action_id    INT NOT NULL,
#       mood         ENUM('happy','neutral','sad') NOT NULL,
#       created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
#       UNIQUE KEY uq_action (action_id),
#       FOREIGN KEY (action_id) REFERENCES actions(action_id) ON DELETE CASCADE
#   );
# ─────────────────────────────────────────────────────────────────────────────

# Ensure risk_model.pkl is in the same directory as main.py
try:
    risk_model = joblib.load("risk_model.pkl")
    print("Chef: ML Risk Model loaded successfully.")
except Exception as e:
    print(f"Chef: Warning! Could not load ML model: {e}")

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
        "already_contacted": 0,
        "no_action":0
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
            t.travel_id, 
            t.customer_id, 
            t.final_destination,
            t.start_date,          -- ADDED: Required for ML 'days_before_travel'
            t.end_date,            -- ADDED: Good practice for debugging
            c.forename, 
            c.optin, 
            c.preferred_language, 
            t.travel_purpose,      -- ADDED: Required for ML feature
            pc.policy_type,
            CASE 
                WHEN DATE_FORMAT(c.dob, '%m-%d') BETWEEN DATE_FORMAT(t.start_date, '%m-%d') AND DATE_FORMAT(t.end_date, '%m-%d')
                THEN 1 ELSE 0 
            END as is_birthday_trip
        FROM travel t
        JOIN customers c ON t.customer_id = c.customer_id
        JOIN policies pc ON c.customer_id = pc.customer_id 
        WHERE :event_date BETWEEN t.start_date AND t.end_date
        AND (
            t.arrival_airport IN (SELECT code FROM LocationHierarchy) OR 
            t.destination_region IN (SELECT code FROM LocationHierarchy)
        )
    """)
    
    impacted = db.execute(matching_sql, {
        "event_date": payload['event_date'],
        "loc": payload['location_code']
    }).fetchall()

    # DEBUG: Let's see exactly what the Sous Chef brought out of the pantry
    if impacted:
        print(f"DEBUG: Columns returned from DB: {impacted[0]._mapping.keys()}")

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
            else: 
                # --- 1. ML DATA PREP ---
                # Accessing via _mapping ensures we don't get the AttributeError again
                t_data = traveler._mapping 
                
                event_date_obj = datetime.strptime(payload['event_date'], "%Y-%m-%d").date()
                
                # Use the mapping to get the date safely
                traveler_start = t_data['start_date']
                if isinstance(traveler_start, str):
                    traveler_start = datetime.strptime(traveler_start, "%Y-%m-%d").date()
                
                days_before_travel = max((traveler_start - event_date_obj).days, 0)
                
                # --- 1. ML DATA PREP ---
                t_data = traveler._mapping 

                # Get the integer directly from the DB (0, 1, or 2)
                # We default to 0 (Standard) if for some reason it's None
                policy_feature = traveler.policy_type if traveler.policy_type is not None else 0
                
                purpose_map = {"leisure": 0, "business": 1}
                travel_purpose_raw = getattr(traveler, 'travel_purpose', 'leisure')
                purpose_feature = purpose_map.get(travel_purpose_raw.lower(), 0)

                model_input = pd.DataFrame([{
                    "severity": payload["severity_level"],
                    "event_type": payload["event_type"],
                    "location_type": payload["location_type"],
                    "days_before_travel": days_before_travel,
                    "policy_type": policy_feature,
                    "travel_purpose": purpose_feature
                }])

                # --- 2. ML PREDICTION ---
                # Get the score from the 'brain'
                risk_probability = risk_model.predict_proba(model_input)[:, 1][0]
                
                # --- 3. GATE 3: DECISION BASED ON ML SCORE ---
                if risk_probability >= 0.7:
                    decision, reason = "notify", "ai_high_risk"
                    counts["eligible"] += 1
                elif risk_probability >= 0.4:
                    decision, reason = "notify_safety_only", "ai_moderate_risk"
                    counts["goodwill"] += 1
                else:
                    decision, reason = "no_action", "ai_low_risk"
                    counts["no_action"] += 1

                # --- 4. AI MESSAGE GENERATION ---
                if decision != "no_action":
                    alt_flight_time = f"{random.randint(11, 21)}:{random.choice(['00', '15', '30', '45'])}"
                    policy_info = POLICY_FEATURES.get(traveler.policy_type, POLICY_FEATURES[0])

                    ai_context = {
                        "forename": traveler.forename,
                        "destination": traveler.final_destination,
                        "event_type": payload['event_type'],
                        "severity": payload['severity_level'],
                        "policy_type": traveler.policy_type,
                        "is_birthday_trip": bool(getattr(traveler, 'is_birthday_trip', False)),
                        "language": traveler.preferred_language,
                        "risk_score": round(risk_probability * 100),
                        "flight_number": getattr(traveler, 'flight_number', 'EA1234'),
                        "dep_airport": getattr(traveler, 'departure_airport', 'LHR'),
                        "alt_time": alt_flight_time,
                        # --- NEW POLICY FACT INJECTION ---
                        "policy_label": policy_info["label"],
                        "medical_limit": policy_info["medical"],
                        "repatriation": policy_info["repatriation"],
                        "cancel_terms": policy_info["cancellation"],
                        "concierge_perk": policy_info["concierge"],
                        "disruption_benefit": policy_info["disruption"]
                    }
                    msg = generate_ai_message(ai_context)
                else:
                    msg = None

        # --- 5. DATABASE RECORDING (End of the loop) ---
        # This records EVERY decision (Notify OR No Action)
        dec_res = db.execute(text("""
            INSERT INTO decisions (event_id, travel_id, decision_type, reason_code)
            VALUES (:eid, :tid, :dt, :rc)
        """), {"eid": event_id, "tid": traveler.travel_id, "dt": decision, "rc": reason})
        
        # This only creates an action if the AI actually wrote a message
        if msg:
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

        "detailed_breakdown": [
            {"category": "AI Prediction: High Risk", "count": counts.get("eligible", 0)},
            {"category": "AI Prediction: Moderate Risk", "count": counts.get("goodwill", 0)},
            {"category": "No Consent (Privacy Block)", "count": counts.get("no_consent", 0)},
            {"category": "Already Contacted (Deduplicated)", "count": counts.get("already_contacted", 0)},
            {"category": "No Coverage (AI Low Risk)", "count": counts.get("no_action", 0)}
        ]
    }

@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    """
    Returns latest notifications for the customer NotificationsScreen.
    Joins through decisions → travels to surface travel_purpose and isRead status.
    """
    
    query = text("""
        SELECT
            a.action_id           AS id,
            a.message,
            a.created_at          AS time,
            a.is_read             AS isRead,
            COALESCE(t.travel_purpose, 'leisure') AS travel_purpose,
            COALESCE(pc.policy_type, 0)            AS policy_type,
            t.customer_id                          AS customer_id
        FROM actions a
        LEFT JOIN decisions d ON a.decision_id = d.decision_id
        LEFT JOIN travel    t ON d.travel_id   = t.travel_id
        LEFT JOIN policies pc ON t.customer_id = pc.customer_id 
        ORDER BY a.created_at DESC
        LIMIT 50
    """)
    
    results = db.execute(query).fetchall()
    rows = []
    for r in results:
        row = dict(r._mapping)
        # Normalise is_read → Python bool (MySQL may return 0/1)
        row["isRead"] = bool(row.get("isRead", 0))
        rows.append(row)
    return rows

@app.patch("/alerts/{alert_id}/read")
def mark_alert_read(alert_id: int, db: Session = Depends(get_db)):
    """Mark a single notification as read when the customer clicks it."""
    result = db.execute(
        text("UPDATE actions SET is_read = 1 WHERE action_id = :id"),
        {"id": alert_id}
    )
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"ok": True, "alert_id": alert_id}


@app.post("/alerts/feedback")
def save_alert_feedback(payload: dict, db: Session = Depends(get_db)):
    """
    Persist the emoji feedback the customer gave for a notification.
    Expects: { "alert_id": int, "mood": "happy" | "neutral" | "sad" }
    """
    valid_moods = {"happy", "neutral", "sad"}
    mood = payload.get("mood", "").lower()
    if mood not in valid_moods:
        raise HTTPException(status_code=422, detail=f"mood must be one of {valid_moods}")

    db.execute(
        text("""
            INSERT INTO alert_feedback (action_id, mood, created_at)
            VALUES (:action_id, :mood, NOW())
            ON DUPLICATE KEY UPDATE mood = :mood, created_at = NOW()
        """),
        {"action_id": payload["alert_id"], "mood": mood}
    )
    db.commit()
    return {"ok": True, "alert_id": payload["alert_id"], "mood": mood}


@app.patch("/customers/{customer_id}/opt-out")
def opt_out_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    Sets optin = 0 for the given customer, preventing future notifications.
    Called when the customer clicks 'Opt Out' in the notification dialog.
    """
    result = db.execute(
        text("UPDATE customers SET optin = 0 WHERE customer_id = :id"),
        {"id": customer_id}
    )
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"ok": True, "customer_id": customer_id, "optin": False}



def get_dashboard(event_id: int, db: Session = Depends(get_db)):
    query = text("""
        SELECT reason_code, COUNT(*) as count
        FROM decisions WHERE event_id = :eid
        GROUP BY reason_code
    """)
    results = db.execute(query, {"eid": event_id}).fetchall()
    
    # Create the dictionary from DB results
    breakdown = {r.reason_code: r.count for r in results}
    
    return {
        "event_id": event_id,
        "detailed_breakdown": [
            {"category": "AI Prediction: High Risk", "count": breakdown.get('ai_high_risk', 0)},
            {"category": "AI Prediction: Moderate Risk", "count": breakdown.get('ai_moderate_risk', 0)},
            {"category": "No Consent (Privacy Block)", "count": breakdown.get('no_consent', 0)},
            {"category": "Already Contacted (Deduplicated)", "count": breakdown.get('already_contacted', 0)},
            {"category": "No Coverage (AI Low Risk)", "count": breakdown.get('ai_low_risk', 0)}
        ]
    }

# ========================
#  TEST BLOCK 
# ========================

@app.get("/test-chef")
def test_chef():
    return {
        "model_loaded": risk_model is not None,
        "model_type": str(type(risk_model))
    }

if __name__ == "__main__":
    # The context block you already created
    test_ctx = {
        "forename": "Boudewijn",
        "destination": "Nice (NCE)",
        "event_type": "Flight Delay",
        "severity": 4,
        "risk_score": 85,
        "policy_type": 2, 
        "policy_label": "Platinum Plus",
        "medical_limit": "Unlimited",
        "repatriation": "Included (Private Jet)",
        "cancel_terms": "Full Refund",
        "concierge_perk": "24/7 Priority Handler",
        "disruption_benefit": "Alternative Flight Search",
        "flight_number": "SN3587",
        "dep_airport": "BRU",
        "alt_time": "14:30",
        "is_birthday_trip": True,
        "language": "Flemish"
    }

    print("\n--- 🛡️ BRUSSELS PROTOCOL: PRIVACY SHIELD TEST ---")
    
    # Execute the function
    final_output = generate_ai_message(test_ctx)
    
    print("\nFINAL REHYDRATED MESSAGE:")
    print(f"[{final_output}]")
    
    # Paranoia Check: Verify the name 'Boudewijn' is actually back in the string
    if "Boudewijn" in final_output:
        print("\n✅ VERIFICATION SUCCESS: PII successfully rehydrated locally.")
    else:
        print("\n❌ VERIFICATION FAILED: Token was not replaced.")