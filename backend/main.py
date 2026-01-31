from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/simulate-event")
def simulate_event(payload: dict):
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
        }
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
