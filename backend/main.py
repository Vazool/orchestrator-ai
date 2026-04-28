import joblib
import pandas as pd
import random
import asyncio
import os
from datetime import datetime
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Custom imports
from database import engine, SessionLocal, get_db
from privacy_engine import demo_vault

# --- 1. BELGIAN POLICY TIERS (Updated) ---

POLICY_FEATURES = {
    0: {
        "label": "Tempo Digital",
        "medical": "up to € 250K",
        "repatriation": "In case of injury or illness",
        "NoGo cancellation": "€500 per trip",
        "Comms method": "Digital only",
        "concierge": "None",
        "disruption": "None"
    },
    1: {
        "label": "Tempo",
        "medical": "up to € 250K",
        "repatriation": "In case of injury or illness",
        "NoGo cancellation": "€500 per trip",
        "Comms method": "Digital + telephone",
        "concierge": "24/7 Helpline",
        "disruption": "None"
    },
    2: {
        "label": "Long Trip Temporary Travel Insurance",
        "medical": "€1.25M",
        "repatriation": "In case of injury or illness",
        "NoGo cancellation": "€10K per trip",
        "Comms method": "Digital + telephone",
        "concierge": "24/7 helpline",
        "disruption": "proactive disruption alerts + auto-claims"
    }
}

app = FastAPI()

# LOCATION HIERARCHY

def load_location_lookup(db):
    rows = db.execute(text("SELECT location_id, parent_location_id, code FROM locations")).fetchall()

    lookup = {}
    code_map = {}

    for r in rows:
        l_id = int(r.location_id)
        raw_parent = r.parent_location_id
        if raw_parent is None or str(raw_parent).strip().upper() == 'NULL':
            parent = None
        else:
            parent = int(raw_parent)

        lookup[l_id] = parent
        code_map[str(r.code).strip().upper()] = l_id

    print(f"--- 📍 LOCATION MAP LOADED: {len(code_map)} codes, {len(lookup)} relationships ---", flush=True)
    return lookup, code_map

def is_location_match(event_loc_id, traveler_loc_code, lookup, code_map):
    if not event_loc_id or not traveler_loc_code:
        return False

    target_id = int(event_loc_id)
    start_code = str(traveler_loc_code).strip().upper()
    current_id = code_map.get(start_code)

    if current_id is None:
        print(f"❌ ERROR: Airport code '{start_code}' not found in Location Maps!", flush=True)
        return False

    visited = set()
    while current_id is not None:
        if int(current_id) == target_id:
            return True
        if current_id in visited:
            break
        visited.add(current_id)
        current_id = lookup.get(int(current_id))

    return False

# Enable CORS for the Frontend

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the "Brain" (ML Model)

try:
    risk_model = joblib.load("risk_model.pkl")
    print("Chef: ML Risk Model loaded successfully.")
except Exception as e:
    print(f"Chef: Warning! Could not load ML model: {e}")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- 2. AI MESSAGE ENGINE (With Brussels Protocol) ---

def generate_ai_message(ctx: dict) -> str:
    real_forename = ctx.get('forename', 'Traveler')
    masked_forename = demo_vault.mask_customer_data(real_forename)

    risk_val = ctx.get('risk_score', 0)
    urgency = "HIGH RISK" if risk_val >= 70 else "MODERATE"

    scout_instruction = ""

    if int(ctx.get('policy_type', 0)) == 2:
        scout_instruction = (
            f"SPECIAL SERVICE UPGRADE: This customer has 'Long Trip Temporary' coverage. "
            f"You MUST include this exact flight scout detail: 'Our scouts have identified a potential "
            f"alternative flight {ctx.get('flight_number', 'EA1234')} at {ctx.get('alt_time', '20:45')}. "
            f"Please contact our assistance team on +32 (0)2 533 75 75 quoting reference {ctx.get('reference_code')} "
            f"to discuss this option.'"
        )
    else:
        scout_instruction = "Do NOT mention alternative flights or proactive scouting."

    prompt = f"""
    Role: Europ Assistance Belgium Concierge.
    User: {masked_forename}. 
    Product: {ctx.get('policy_label')} (Cover: {ctx.get('medical_limit')}, Cancellation: {ctx.get('cancel_terms')}).
    Event: {ctx.get('event_type')} in {ctx.get('destination')}. Risk: {risk_val}%.

    {scout_instruction}

    Task: Write a {urgency} alert in {ctx.get('language', 'English')}.
    Constraints: 
    - Max 3 sentences for Standard/Tempo. 
    - Max 4 sentences for Long Trip Temporary.
    - Use {masked_forename} exactly.
    - Never imply re-booking costs are covered.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise insurance assistant. Follow the 'SPECIAL SERVICE UPGRADE' or 'Do NOT' instructions perfectly."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )

        return demo_vault.rehydrate_message(response.choices[0].message.content.strip())

    except Exception as e:
        return f"Safety Alert: {ctx['event_type']} near {ctx['destination']}. {real_forename}, please check your app."

# --- 3. THE PARALLEL WORKER (The "Sous Chef") ---

async def process_traveler_notification(traveler, payload, event_id, location_lookup, code_to_location):
    async_db = SessionLocal()
    try:
        # 1. Convert "NCE" to the numeric ID
        payload_code = payload.get("location_code")
        payload_location_id = code_to_location.get(payload_code)

        if payload_location_id is None:
            return "location_not_found"

        # 2. Check if the traveler's airport matches the event location (or its parents)
        affected = is_location_match(
            payload_location_id,
            traveler.arrival_airport,
            location_lookup,
            code_to_location
        )

        if not affected:
            async_db.execute(text("""
                INSERT INTO decisions (event_id, travel_id, decision_type, reason_code) 
                VALUES (:eid, :tid, 'no_action', 'not_impacted')
            """), {"eid": event_id, "tid": traveler.travel_id})
            await async_db.commit()
            return "not_impacted"

        # --- STAGE 0. STANDARDIZE POLICY TYPE ---
        p_type = int(traveler.policy_type) if traveler.policy_type is not None else 0
        policy_info = POLICY_FEATURES.get(p_type, POLICY_FEATURES[0])

        # --- STAGE 1: PRIVACY CHECK ---
        if int(traveler.optin or 0) == 0:
            async_db.execute(text("""
                INSERT INTO decisions (event_id, travel_id, decision_type, reason_code) 
                VALUES (:eid, :tid, 'no_action', 'no_consent')
            """), {"eid": event_id, "tid": traveler.travel_id})
            async_db.commit()
            return "no_consent"

        # --- STAGE 2: DEDUPLICATION ---
        dedup_sql = text("""
            SELECT COUNT(*) FROM decisions d
            JOIN events e ON d.event_id = e.event_id
            WHERE d.travel_id = :tid 
                AND e.location_code = :loc 
                AND d.decision_type != 'no_action'
                AND e.event_date >= DATE_SUB(:ed, INTERVAL 7 DAY)
                AND d.event_id != :current_eid
        """)

        is_dup = async_db.execute(dedup_sql, {
            "tid": traveler.travel_id, "loc": payload['location_code'],
            "ed": payload['event_date'], "current_eid": event_id
        }).scalar()

        if is_dup > 0:
            async_db.execute(text("""
                INSERT INTO decisions (event_id, travel_id, decision_type, reason_code) 
                VALUES (:eid, :tid, 'no_action', 'already_contacted')
            """), {"eid": event_id, "tid": traveler.travel_id})
            async_db.commit()
            return "already_contacted"

        # --- STAGE 3: ML RISK SCORING ---
        t_map = traveler._mapping
        e_date = datetime.strptime(payload['event_date'], "%Y-%m-%d").date()
        days_diff = max((t_map['start_date'] - e_date).days, 0)

        model_input = pd.DataFrame([{
            "severity": payload["severity_level"],
            "event_type": payload["event_type"],
            "location_type": payload["location_type"],
            "days_before_travel": days_diff,
            "policy_type": p_type,
            "travel_purpose": 0
        }])

        risk_prob = risk_model.predict_proba(model_input)[:, 1][0]

        if risk_prob >= 0.7:
            decision, reason = "notify", "ai_high_risk"
        elif risk_prob >= 0.4:
            decision, reason = "notify_safety_only", "ai_moderate_risk"
        else:
            decision, reason = "no_action", "ai_low_risk"

        # --- BUSINESS TRAVELLER OVERRIDE ---
        # Business travellers are always notified regardless of ML score
        travel_purpose = str(t_map.get("travel_purpose") or "").lower()
        if travel_purpose in ["business", "work", "conference"]:
            print(f"💼 BUSINESS OVERRIDE: {traveler.forename} — always notified", flush=True)
            decision = "notify"
            reason = "ai_high_risk"

        # --- STAGE 4: AI GENERATION (With Scout Logic) ---
        msg = None
        if decision != "no_action":
            reference_code = f"EA-{event_id}-{random.randint(1000, 9999)}"
            if p_type == 2:
                print(f"💎 SCOUT ACTIVATED for {traveler.forename}")

            ctx = {
                "forename": traveler.forename,
                "destination": traveler.final_destination,
                "event_type": payload['event_type'],
                "severity": payload['severity_level'],
                "risk_score": round(risk_prob * 100),
                "language": traveler.preferred_language,
                "policy_label": policy_info["label"],
                "medical_limit": policy_info["medical"],
                "cancel_terms": policy_info["NoGo cancellation"],
                "policy_type": p_type,
                "disruption": policy_info.get("disruption"),
                "flight_number": "EA" + str(random.randint(1000, 9999)),
                "dep_airport": traveler.arrival_airport or "NCE",
                "alt_time": "20:45",
                "reference_code": reference_code
            }
            msg = await asyncio.to_thread(generate_ai_message, ctx)

        # --- STAGE 5: RECORDING ---
        res = async_db.execute(text("""
            INSERT INTO decisions (event_id, travel_id, decision_type, reason_code) 
            VALUES (:eid, :tid, :dt, :rc)
        """), {"eid": event_id, "tid": traveler.travel_id, "dt": decision, "rc": reason})

        if msg:
            async_db.execute(text("""
                INSERT INTO actions (decision_id, channel_type, action_status, message) 
                VALUES (:did, 'email', 'queued', :msg)
            """), {"did": res.lastrowid, "msg": msg})

        async_db.commit()
        return reason

    except Exception as e:
        print(f"Worker Error: {e}")
        return "error"
    finally:
        async_db.close()


# --- 4. THE MAIN ROUTES ---

@app.post("/simulate-event")
async def simulate_event(data: dict, db: Session = Depends(get_db)):
    location_lookup, code_to_location = load_location_lookup(db)

    # 1. Date formatting logic
    raw_date = data.get('event_date')
    if '/' in raw_date:
        day, month, year = raw_date.split('/')
        event_date = f"{year}-{month}-{day}"
    else:
        event_date = raw_date

    # 2. Record the Event in the DB
    event_sql = text("""
        INSERT INTO events (event_type, location_type, location_code, event_date, severity_level, source)
        VALUES (:et, :lt, :lc, :ed, :sl, :src)
    """)

    res = db.execute(event_sql, {
        "et": data.get('event_type'),
        "lt": data.get('location_type'),
        "lc": data.get('location_code'),
        "ed": event_date,
        "sl": data.get('severity_level'),
        "src": data.get('source', 'simulator')
    })
    event_id = res.lastrowid
    db.commit()

    # --- 3. IMPACT ZONE EXPANSION ---
    target_code = data.get('location_code', 'FR').strip().upper()
    target_id = code_to_location.get(target_code)

    affected_ids = {target_id} if target_id else set()
    expanded = True
    while expanded:
        expanded = False
        for child_id, parent_id in location_lookup.items():
            if parent_id in affected_ids and child_id not in affected_ids:
                affected_ids.add(child_id)
                expanded = True

    id_to_code = {v: k for k, v in code_to_location.items()}
    affected_codes = [id_to_code[i] for i in affected_ids if i in id_to_code]

    if not affected_codes:
        affected_codes = [target_code]

    print(f"--- 📡 BROADCASTING TO: {affected_codes} ---", flush=True)

    # --- 4. FIND IMPACTED TRAVELERS ---
    # ✅ CHANGE: Added t.travel_purpose to the SELECT so business override works
    impacted = db.execute(text("""
        SELECT t.travel_id, t.customer_id, t.final_destination, t.start_date, t.end_date,
               t.arrival_airport, t.travel_purpose,
               c.forename, c.optin, c.preferred_language, pc.policy_type
        FROM travel t 
        JOIN customers c ON t.customer_id = c.customer_id 
        JOIN policies pc ON c.customer_id = pc.customer_id
        WHERE :ed BETWEEN t.start_date AND t.end_date 
        AND (UPPER(t.arrival_airport) IN :codes OR UPPER(t.destination_region) IN :codes)
    """), {
        "ed": event_date,
        "codes": tuple(affected_codes)
    }).fetchall()

    # Parallel processing
    sem = asyncio.Semaphore(10)

    async def task(t):
        async with sem:
            return await process_traveler_notification(
                t, data, event_id, location_lookup, code_to_location
            )

    results = await asyncio.gather(*[task(t) for t in impacted])

    # 1. Initialize the counters
    counts = {
        "eligible": 0,
        "goodwill": 0,
        "no_consent": 0,
        "already_contacted": 0,
        "no_action": 0
    }

    # 2. Map the worker reason_codes back to the UI categories
    reason_to_category = {
        "ai_high_risk": "eligible",
        "ai_moderate_risk": "goodwill",
        "no_consent": "no_consent",
        "already_contacted": "already_contacted",
        "ai_low_risk": "no_action"
    }

    for reason in results:
        category = reason_to_category.get(reason)
        if category in counts:
            counts[category] += 1

    # 4. Calculate the summary for the UI
    total_portfolio = 1000
    evaluated = len(impacted)
    notified = counts.get("eligible", 0) + counts.get("goodwill", 0)
    not_impacted = total_portfolio - evaluated

    print(f"\n--- 🛡️ BRUSSELS PROTOCOL: RESULTS FOR {data.get('location_code')} ---")
    print(f"Total Found in Database: {len(impacted)}")
    print(f"Privacy Blocks (Opt-out): {counts.get('no_consent', 0)}")
    print(f"Deduplicated (Already sent): {counts.get('already_contacted', 0)}")
    print(f"AI Notifications Queued: {counts.get('eligible', 0) + counts.get('goodwill', 0)}")
    print(f"Low Risk (No Action): {counts.get('no_action', 0)}")
    print("---------------------------------------------------\n")

    return {
        "event_id": event_id,
        "total_records": total_portfolio,
        "customers_evaluated": evaluated,
        "notifications_created": notified,
        "customers_not_impacted": not_impacted,
        "detailed_breakdown": [
            {"category": "AI Prediction: High Risk",           "count": counts.get("eligible", 0)},
            {"category": "AI Prediction: Moderate Risk",       "count": counts.get("goodwill", 0)},
            {"category": "No Consent (Privacy Block)",         "count": counts.get("no_consent", 0)},
            {"category": "Already Contacted (Deduplicated)",   "count": counts.get("already_contacted", 0)},
            {"category": "No Coverage (AI Low Risk)",          "count": counts.get("no_action", 0)}
        ]
    }


# --- 5. DASHBOARD ROUTE (Real data) ---

@app.get("/dashboard")
def get_dashboard(event_id: int, db: Session = Depends(get_db)):
    # Get the event itself
    event = db.execute(text("""
        SELECT event_id, event_type, location_code, event_date, severity_level
        FROM events WHERE event_id = :eid
    """), {"eid": event_id}).fetchone()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Decision breakdown by type/reason
    breakdown = db.execute(text("""
        SELECT decision_type, reason_code, COUNT(*) as count
        FROM decisions WHERE event_id = :eid
        GROUP BY decision_type, reason_code
    """), {"eid": event_id}).fetchall()

    # All notifications sent for this event
    notifications = db.execute(text("""
        SELECT a.action_id, a.message, a.action_status, a.created_at,
               t.customer_id, d.reason_code
        FROM actions a
        JOIN decisions d ON a.decision_id = d.decision_id
        JOIN travel t ON d.travel_id = t.travel_id
        WHERE d.event_id = :eid
        ORDER BY a.created_at DESC
    """), {"eid": event_id}).fetchall()

    # REAL travel purpose breakdown 
    purpose = db.execute(text("""
        SELECT t.travel_purpose, COUNT(*) as count
        FROM decisions d
        JOIN travel t ON d.travel_id = t.travel_id
        WHERE d.event_id = :eid
        GROUP BY t.travel_purpose
    """), {"eid": event_id}).fetchall()

    # REAL policy tier breakdown 
    policy = db.execute(text("""
        SELECT pc.policy_type, COUNT(*) as count
        FROM decisions d
        JOIN travel t ON d.travel_id = t.travel_id
        JOIN policies pc ON t.customer_id = pc.customer_id
        WHERE d.event_id = :eid
        GROUP BY pc.policy_type
    """), {"eid": event_id}).fetchall()

    policy_labels = {0: "Tempo Digital", 1: "Tempo", 2: "Long Trip Temporary"}

    return {
        "event":             dict(event._mapping),
        "breakdown":         [dict(r._mapping) for r in breakdown],
        "notifications":     [dict(r._mapping) for r in notifications],
        "total_notified":    len(notifications),
        "purpose_breakdown": [
            {"category": r.travel_purpose or "Unknown", "count": r.count}
            for r in purpose
        ],
        "policy_breakdown": [
            {"category": policy_labels.get(r.policy_type, f"Tier {r.policy_type}"), "count": r.count}
            for r in policy
        ],
    }


# --- 6. UI ENDPOINTS ---

@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    query = text("""
        SELECT a.action_id AS id, a.message, a.created_at AS time, a.is_read AS isRead, t.customer_id
        FROM actions a 
        JOIN decisions d ON a.decision_id = d.decision_id 
        JOIN travel t ON d.travel_id = t.travel_id
        ORDER BY a.created_at DESC LIMIT 50
    """)
    return [dict(r._mapping, isRead=bool(r._mapping.get('isRead', 0))) for r in db.execute(query)]

@app.patch("/alerts/{alert_id}/read")
def mark_read(alert_id: int, db: Session = Depends(get_db)):
    db.execute(text("UPDATE actions SET is_read = 1 WHERE action_id = :id"), {"id": alert_id})
    db.commit()
    return {"ok": True}

@app.patch("/customers/{customer_id}/opt-out")
def opt_out(customer_id: int, db: Session = Depends(get_db)):
    db.execute(text("UPDATE customers SET optin = 0 WHERE customer_id = :id"), {"id": customer_id})
    db.commit()
    return {"ok": True}

@app.post("/alerts/feedback")
def submit_feedback(payload: dict, db: Session = Depends(get_db)):
    alert_id = payload.get('action_id') or payload.get('alert_id')
    mood = payload.get('mood')

    print(f"DEBUG: Feedback hit! Alert: {alert_id}, Mood: {mood}")

    if not alert_id or not mood:
        raise HTTPException(status_code=400, detail="Missing alert_id or mood")

    try:
        query = text("""
            INSERT INTO alert_feedback (action_id, mood) 
            VALUES (:aid, :mood)
            ON DUPLICATE KEY UPDATE mood = :mood
        """)
        db.execute(query, {"aid": alert_id, "mood": mood})
        db.commit()
        return {"ok": True}
    except Exception as e:
        db.rollback()
        print(f"SQL Error in feedback: {e}")
        raise HTTPException(status_code=500, detail="Database error")

@app.post("/admin/reset")
def reset_demo(db: Session = Depends(get_db)):
    try:
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        db.execute(text("TRUNCATE TABLE actions"))
        db.execute(text("TRUNCATE TABLE decisions"))
        db.execute(text("TRUNCATE TABLE events"))
        db.execute(text("TRUNCATE TABLE alert_feedback"))
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

        db.commit()
        return {"status": "ok"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Reset failed")