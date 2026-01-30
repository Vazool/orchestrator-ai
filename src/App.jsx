import { useState } from "react";
import NotificationsScreen from "./components/NotificationsScreen";
import OperatorScreen from "./components/OperatorScreen";

function App() {
  const [view, setView] = useState("customer");

  return (
    <div>
      <div>
        <button onClick={() => setView("customer")}>
          Customer View
        </button>
        <button onClick={() => setView("operator")}>
          Operator Console
        </button>
      </div>

      {view === "customer" && <NotificationsScreen />}
      {view === "operator" && <OperatorScreen />}
    </div>
  );
}

export default App;
