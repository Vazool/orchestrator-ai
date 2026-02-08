import { useState } from "react";

const EVENT_TYPES = [
  "weather_warning",
  "flight_disruption",
  "gov_advice_change",
  "major_event"
];

const LOCATION_TYPES = ["country", "admin_area", "city", "airport", "flight"];

// For v0 keep this simple and demo-friendly.
// Later we can fetch these from the backend/DB.
const LOCATION_CODES = {
  country: ["FR", "GB"],
  admin_area: ["FR-75", "FR-13", "FR-06"],
  city: ["PAR", "MRS", "NCE"],
  airport: ["CDG", "ORY", "MRS", "NCE"],
  flight: ["BA204:2026-02-12"]
};

function OperatorScreen() {
  const [eventType, setEventType] = useState("weather_warning");
  const [eventDate, setEventDate] = useState("2026-02-12");
  const [locationType, setLocationType] = useState("airport");
  const [locationCode, setLocationCode] = useState("CDG");
  const [severityLevel, setSeverityLevel] = useState(4);

  const [simulateResult, setSimulateResult] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const onLocationTypeChange = (newType) => {
    setLocationType(newType);
    const firstCode = (LOCATION_CODES[newType] && LOCATION_CODES[newType][0]) || "";
    setLocationCode(firstCode);
  };

  const simulateEvent = async () => {
    setError(null);
    setLoading(true);
    setDashboard(null);

    const payload = {
      event_type: eventType,
      source: "simulator",
      event_date: eventDate,
      location_type: locationType,
      location_code: locationCode,
      severity_level: Number(severityLevel),
      payload: {
        headline: "Simulated event (v0)"
      }
    };

    try {
      const res = await fetch("http://localhost:5000/simulate-event", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error("simulate-event failed");
      const simData = await res.json();
      setSimulateResult(simData);

      const dashRes = await fetch(
        `http://localhost:5000/dashboard?event_id=${simData.event_id}`
      );
      if (!dashRes.ok) throw new Error("dashboard fetch failed");
      const dashData = await dashRes.json();
      setDashboard(dashData);
    } catch (e) {
      setError("Failed to simulate event or fetch dashboard");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2>Operator Console</h2>
      <div style = {styles.box}>
        <h3>API Simulation</h3>

        <div>
          <label>
            Event type{" "}
            <select value={eventType} onChange={(e) => setEventType(e.target.value)}>
              {EVENT_TYPES.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </label>
        </div>

        <div>
          <label>
            Event date{" "}
            <input
              type="date"
              value={eventDate}
              onChange={(e) => setEventDate(e.target.value)}
            />
          </label>
        </div>

        <div>
          <label>
            Location type{" "}
            <select
              value={locationType}
              onChange={(e) => onLocationTypeChange(e.target.value)}
            >
              {LOCATION_TYPES.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </label>
        </div>

        <div>
          <label>
            Location code{" "}
            <select
              value={locationCode}
              onChange={(e) => setLocationCode(e.target.value)}
            >
              {(LOCATION_CODES[locationType] || []).map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </label>
        </div>

        <div>
          <label>
            Severity (1–5){" "}
            <input
              type="number"
              min="1"
              max="5"
              value={severityLevel}
              onChange={(e) => setSeverityLevel(e.target.value)}
            />
          </label>
        </div>

        <button onClick={simulateEvent} disabled={loading || !locationCode}>
          {loading ? "Running..." : "Simulate Event"}
        </button>

        {error && <p>{error}</p>}

        {simulateResult && (
          <div>
            <h3>Simulation Result</h3>
            <p>Event ID: {simulateResult.event_id}</p>
            <hr />
            {/* New Headline Totals */}
            <p><strong>Total Portfolio:</strong> {simulateResult.total_records}</p>
            <p><strong>Customers Evaluated:</strong> {simulateResult.customers_evaluated}</p>
            <p><strong>Notifications Created:</strong> {simulateResult.notifications_created}</p>
            <p><strong>Customers Not Impacted:</strong> {simulateResult.customers_not_impacted}</p>

            {simulateResult.simulated_payload && (
              <>
                <h4>Simulated payload (echo)</h4>
                <pre>{JSON.stringify(simulateResult.simulated_payload, null, 2)}</pre>
              </>
            )}
          </div>
        )}

        {dashboard && (
          <div>
            <h3>Commissioner Dashboard (v0)</h3>

            <details>
              <summary>View raw dashboard data</summary>
              <pre>{JSON.stringify(dashboard, null, 2)}</pre>
            </details>
          </div>
        )}
      </div>
    </div>
  );
}

const styles= {
  container: {
    display:"flex",
    flexDirection:"column",
    justifyContent:"center",
    alignItems:"center",
    width:"50%",
    height:"100%",
    backgroundColor: "#fff",
    padding: "24px",
    borderRadius: "12px",
    boxShadow: "0 10px 25px rgba(0,0,0,0.08)",
    fontSize:"2rem",
    marginLeft: "50vh"
  

  },
  box:{
    maxWidth: "600px",
    width: "100%", 
    height:"100%",
    fontSize:"1.5rem",
  }

}

export default OperatorScreen;
