from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

LAST_SIMULATED = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/simulate-event")
def simulate_event(payload: dict):
    global LAST_SIMULATED
    LAST_SIMULATED = payload
    
    return {
        "event_id": 101,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "customers_evaluated": 12,
        "notifications_created": 7,
        "decision_breakdown": {
            "eligible": 6,
            "goodwill_alert": 1,
            "not_travelling": 2,
            "no_consent": 3,
            "no_coverage": 0
        },
        "simulated_payload": payload
    }

@app.get("/alerts")
def get_alerts():
    return [
        {
            "id": 9001,
            "message": "Hi Alice. Severe weather is forecast at Paris CDG on 12 Feb.",
            "time": datetime.utcnow().isoformat() + "Z",
            "isRead": False
        }
    ]

@app.get("/dashboard")
def get_dashboard(event_id: int):
    event = LAST_SIMULATED or {}
    
    return {
        "event": {
            "event_id": event_id,
            "event_type": event.get("event_type", "weather_warning"),
            "event_date": event.get("event_date", "2026-02-12"),
            "location_type": event.get("location_type", "airport"),
            "location_code": event.get("location_code", "CDG"),
            "severity_level": event.get("severity_level", 4),
        },
        "metrics": {
            "customers_evaluated": 12,
            "notifications_created": 7
        },
        "decision_breakdown": [
            {"reason_code": "eligible", "count": 6},
            {"reason_code": "goodwill_alert", "count": 1},
            {"reason_code": "not_travelling", "count": 2},
            {"reason_code": "no_consent", "count": 3},
            {"reason_code": "no_coverage", "count": 0}
        ],
        "channel_breakdown": [
            {"channel_type": "app", "count": 5},
            {"channel_type": "email", "count": 2},
            {"channel_type": "other", "count": 0}
        ]
    }
