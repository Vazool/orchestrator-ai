from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import json

# Your custom connection logic
from database import engine, SessionLocal, get_db

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
        INSERT INTO Events (event_type, location_type, location_code, event_date, severity_level, source)
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

    # 2. Matching Logic (Recursive Hierarchy)
    matching_sql = text("""
        WITH RECURSIVE LocationHierarchy AS (
            SELECT location_id, code FROM Locations WHERE code = :loc
            UNION ALL
            SELECT l.location_id, l.code
            FROM Locations l
            INNER JOIN LocationHierarchy lh ON l.parent_location_id = lh.location_id
        )
        SELECT t.travel_id, t.customer_id, c.forename, c.optin, pc.policy_type
        FROM Travel t
        JOIN Customers c ON t.customer_id = c.customer_id
        JOIN PolicyCoverage pc ON c.customer_id = pc.customer_id
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

    # 3. Decision Engine Logic
    for traveler in impacted:
        # GATE 1: PRIVACY (Consent Check)
        if not traveler.optin:
            decision, reason = "no_action", "no_consent"
            counts["no_consent"] += 1
            msg = None
        
        else:
            # GATE 2: DEDUPLICATION (State-Awareness Check)
            # Check if this customer got an alert for this TYPE and LOCATION in the last 7 days
            dedup_sql = text("""
                SELECT COUNT(*) FROM Decisions d
                JOIN Events e ON d.event_id = e.event_id
                WHERE d.travel_id = :tid 
                  AND e.event_type = :et 
                  AND e.location_code = :loc 
                  AND d.decision_type != 'no_action'
                  AND e.event_date >= DATE_SUB(:ed, INTERVAL 7 DAY)
                  AND d.event_id != :current_eid
            """)
            is_dup = db.execute(dedup_sql, {
                "tid": traveler.travel_id, 
                "et": payload['event_type'],
                "loc": payload['location_code'], 
                "ed": payload['event_date'],
                "current_eid": event_id
            }).scalar()

            if is_dup > 0:
                decision, reason = "no_action", "already_contacted"
                counts["already_contacted"] += 1
                msg = None
            
            # GATE 3: POLICY ELIGIBILITY
            elif traveler.policy_type == 'platinum_all' or traveler.policy_type == payload['event_type']:
                decision, reason = "notify", "eligible"
                counts["eligible"] += 1
                msg = f"[Event #{event_id}] Your {traveler.policy_type} policy covers this {payload['event_type']}."
            
            # GATE 4: GOODWILL ALERT
            else:
                decision, reason = "notify_safety_only", "goodwill_alert"
                counts["goodwill"] += 1
                msg = f"[Event #{event_id}] Safety Alert: {payload['event_type']} detected on your route."

        # Insert into Decisions
        dec_res = db.execute(text("""
            INSERT INTO Decisions (event_id, travel_id, decision_type, reason_code)
            VALUES (:eid, :tid, :dt, :rc)
        """), {"eid": event_id, "tid": traveler.travel_id, "dt": decision, "rc": reason})
        
        # Insert into Actions (Only if a message was generated)
        if msg:
            db.execute(text("""
                INSERT INTO Actions (decision_id, channel_type, action_status, message)
                VALUES (:did, 'email', 'queued', :msg)
            """), {"did": dec_res.lastrowid, "msg": msg})

    db.commit()

    # THE RECONCILIATION SUMMARY
    evaluated_count = len(impacted)
    not_at_risk = TOTAL_PORTFOLIO - evaluated_count

    return {
            # Headline Labels for the UI
            "event_id": event_id,
            "total_records": TOTAL_PORTFOLIO,              # The 200
            "customers_evaluated": evaluated_count,         # The 36
            "notifications_created": counts["eligible"] + counts["goodwill"], # The 33
            "customers_not_impacted": not_at_risk,          # The 164

            # Detailed Dashboard Data (for the expandable JSON view)
            "summary": {
                "total_portfolio": TOTAL_PORTFOLIO,
                "not_at_risk_count": not_at_risk,
                "evaluated_in_zone": evaluated_count
            },
            "breakdown": {
                "notified_eligible": counts["eligible"],
                "notified_goodwill": counts["goodwill"],
                "blocked_privacy": counts["no_consent"],
                "blocked_duplicate": counts["already_contacted"]
            }
        }

@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    # Returns latest notifications for CJ's NotificationScreen
    query = text("SELECT action_id as id, message, created_at as time FROM Actions ORDER BY created_at DESC LIMIT 50")
    results = db.execute(query).fetchall()
    return [dict(r._mapping) for r in results]

@app.get("/dashboard")
def get_dashboard(event_id: int, db: Session = Depends(get_db)):
    query = text("""
        SELECT reason_code, COUNT(*) as count
        FROM Decisions WHERE event_id = :eid
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
