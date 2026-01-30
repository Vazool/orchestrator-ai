import { useState } from "react";

function OperatorScreen() {
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const simulateEvent = async () => {
    setError(null);

    const payload = {
      event_type: "weather_warning",
      source: "simulator",
      event_date: "2026-02-12",
      location_type: "airport",
      location_code: "CDG",
      severity_level: 4,
      payload: {
        headline: "Severe weather expected"
      }
    };

    try {
      const res = await fetch("http://localhost:5000/simulate-event", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error("API error");
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError("Failed to simulate event");
    }
  };

  return (
    <div>
      <h2>Operator Console</h2>

      <button onClick={simulateEvent}>
        Simulate Event
      </button>

      {error && <p>{error}</p>}

      {result && (
        <div>
          <h3>Event Result</h3>
          <p>Event ID: {result.event_id}</p>
          <p>Customers evaluated: {result.customers_evaluated}</p>
          <p>Notifications created: {result.notifications_created}</p>

          <h4>Decision breakdown</h4>
          <ul>
            {Object.entries(result.decision_breakdown).map(
              ([reason, count]) => (
                <li key={reason}>
                  {reason}: {count}
                </li>
              )
            )}
          </ul>
        </div>
      )}
    </div>
  );
}

export default OperatorScreen;
