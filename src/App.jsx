import { useState } from "react";
import NotificationsScreen from "./components/NotificationsScreen";
import OperatorScreen from "./components/OperatorScreen";
import europLogo from "./assets/europ-logo.png";

function App() {
  const [view, setView] = useState("customer");

  return (
    <div style={styles.root}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@600;700;800&display=swap');
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        html, body { background: #f4f6fb; }
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-track { background: #eef1f8; }
        ::-webkit-scrollbar-thumb { background: #c8d0e8; border-radius: 3px; }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes slideIn {
          from { opacity: 0; transform: translateY(12px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulseRed {
          0%, 100% { opacity: 1; }
          50%       { opacity: 0.45; }
        }
        @keyframes fadeRight {
          from { opacity: 0; transform: translateX(28px); }
          to   { opacity: 1; transform: translateX(0); }
        }
        @keyframes fadeLeft {
          from { opacity: 0; transform: translateX(-28px); }
          to   { opacity: 1; transform: translateX(0); }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: scale(0.96); }
          to   { opacity: 1; transform: scale(1); }
        }
      `}</style>

      <header style={styles.header}>
        <div style={styles.brand}>
          <img src={europLogo} alt="Europ Assistance" style={styles.logo} />
          <div style={styles.brandDivider} />
          <span style={styles.brandPill}>Travel Protection Platform</span>
        </div>

        <nav style={styles.nav}>
          <button
            style={{ ...styles.navBtn, ...(view === "customer" ? styles.navActive : {}) }}
            onClick={() => setView("customer")}
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
            </svg>
            Customer View
          </button>
          <button
            style={{ ...styles.navBtn, ...(view === "operator" ? styles.navActive : {}) }}
            onClick={() => setView("operator")}
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/>
            </svg>
            Operator Console
          </button>
        </nav>
      </header>

      <main style={styles.main}>
        {view === "customer" && <NotificationsScreen />}
        {view === "operator" && <OperatorScreen />}
      </main>
    </div>
  );
}

const styles = {
  root: {
    minHeight: "100vh",
    backgroundColor: "#f4f6fb",
    fontFamily: "'Inter', sans-serif",
    color: "#1a1a2e",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "0 2.5rem",
    height: "72px",
    background: "#ffffff",
    borderBottom: "1px solid #e2e8f0",
    position: "sticky",
    top: 0,
    zIndex: 100,
    boxShadow: "0 1px 8px rgba(0,0,0,0.06)",
  },
  brand: {
    display: "flex",
    alignItems: "center",
    gap: "14px",
  },
  logo: {
    height: "52px",
    width: "auto",
    objectFit: "contain",
  },
  brandDivider: {
    width: "1px",
    height: "28px",
    background: "#e2e8f0",
  },
  brandPill: {
    fontSize: "0.72rem",
    fontWeight: 600,
    color: "#1d4ed8",
    background: "#EFF6FF",
    border: "1px solid #BFDBFE",
    padding: "4px 10px",
    borderRadius: "20px",
    letterSpacing: "0.04em",
    textTransform: "uppercase",
    fontFamily: "'Inter', sans-serif",
  },
  nav: {
    display: "flex",
    gap: "4px",
    background: "#f1f5f9",
    padding: "4px",
    borderRadius: "10px",
  },
  navBtn: {
    display: "flex",
    alignItems: "center",
    gap: "7px",
    background: "transparent",
    border: "none",
    color: "#64748b",
    padding: "7px 16px",
    borderRadius: "7px",
    cursor: "pointer",
    fontSize: "0.83rem",
    fontFamily: "'Inter', sans-serif",
    fontWeight: 500,
    transition: "all 0.18s ease",
    whiteSpace: "nowrap",
  },
  navActive: {
    background: "#ffffff",
    color: "#1d4ed8",
    boxShadow: "0 1px 4px rgba(0,0,0,0.1)",
    fontWeight: 600,
  },
  main: { minHeight: "calc(100vh - 72px)" },
};

export default App;
