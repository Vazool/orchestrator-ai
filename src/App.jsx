import { useState } from "react";
import NotificationsScreen from "./components/NotificationsScreen";
import OperatorScreen from "./components/OperatorScreen";

function App() {
  const [view, setView] = useState("customer");

  return (
    <div style = {styles.container}>
      <div style ={styles.header}>
        <div style = {styles.buttons}>
          <button onClick={() => setView("customer")}>
            Customer View
          </button>
          <button onClick={() => setView("operator")}>
            Operator Console
          </button>
        </div>
      </div>
      {view === "customer" && <NotificationsScreen />}
      {view === "operator" && <OperatorScreen />}
    </div>
  );
}
const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    minHeight: "100vh",
    width: "100%",
    backgroundColor: "#FAF9F6",
    fontFamily: "system-ui, sans-serif",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "16px 24px",
    backgroundColor: "#4f46e5",
    color: "#fff",
    padding:"2rem"
  },
  box: {
    flex: 0.5, 
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#FAF9F6",
  },
  buttons:{
    display: "flex",
    gap:"20px"
  }
};

export default App;
