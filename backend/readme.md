🌍 Travel Orchestrator PoC
State-Aware Decision Engine & Mass Notification Simulator

This project demonstrates a high-scale (1,000+ traveler) orchestration engine that monitors regional events and automates policy-led notifications while respecting GDPR consent.

🚀 Quick Start (Demo Setup)
1. Backend Setup (FastAPI)
>>cd backend
>>pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --reload

# Copy .env.example to .env and fill in your MySQL credentials

# Ensure your MySQL server is running!

2. Database Population
Run the mass-seeder to generate the 1,000-person test environment:
>> python customer_mass_seeder.py

3. Frontend Setup (Vite)
>>cd frontend (use root... currently no "frontend" folder)
>>npm install
>>npm run dev

🏗️ Technical Architecture
Recursive Geofencing: Uses Recursive CTEs to waterfall regional events (e.g., Ile-de-France) down to specific airports/locations.

State-Awareness: Prevents alert fatigue by deduplicating notifications against a persistent Decisions audit trail.

Policy-Led Logic: Automatically differentiates messaging for Platinum vs. Basic cover tiers.

GDPR Compliance: Built-in privacy gates that block notifications for users without active optin status.

🛠️ Tech Stack

Frontend: React + Vite + Tailwind

Backend: FastAPI (Python 3.10+)

Database: MySQL + SQLAlchemy

Logic: Recursive SQL, Deterministic Decision Matrices