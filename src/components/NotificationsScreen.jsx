import { useState, useEffect } from 'react';
import NotificationItem from './NotificationItem';

/* Derive travel type from backend data or fall back to a deterministic default */
function getTravelType(alert) {
  if (alert.travel_purpose) {
    const p = alert.travel_purpose.toLowerCase();
    if (p.includes("business") || p.includes("work") || p.includes("conference")) return "business";
    return "leisure";
  }
  if (alert.policy_tier) {
    const t = alert.policy_tier.toLowerCase();
    if (t.includes("business") || t.includes("corporate")) return "business";
  }
  // Fallback: alternate deterministically so demo looks varied
  return alert.id % 2 === 0 ? "business" : "leisure";
}

function NotificationsScreen() {
  const [alerts, setAlerts]             = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [lastUpdated, setLastUpdated]   = useState(null);
  const [direction, setDirection]       = useState("right");
  const [animKey, setAnimKey]           = useState(0);

  const fetchAlerts = () => {
    fetch("/api/alerts")
      .then(res => res.json())
      .then(data => {
        setAlerts(data);
        setLastUpdated(new Date());
      })
      .catch(err => console.error("Error fetching alerts:", err));
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (alerts.length > 0 && currentIndex >= alerts.length) {
      setCurrentIndex(alerts.length - 1);
    }
  }, [alerts]);

  const goNext = () => {
    if (currentIndex < alerts.length - 1) {
      setDirection("right");
      setAnimKey(k => k + 1);
      setCurrentIndex(i => i + 1);
    }
  };

  const goPrev = () => {
    if (currentIndex > 0) {
      setDirection("left");
      setAnimKey(k => k + 1);
      setCurrentIndex(i => i - 1);
    }
  };

  const formatLastUpdated = () => {
    if (!lastUpdated) return null;
    const secs = Math.round((Date.now() - lastUpdated) / 1000);
    return secs < 5 ? "just now" : `${secs}s ago`;
  };

  const current = alerts[currentIndex] || null;
  const unreadCount = alerts.filter(a => !a.isRead).length;

  return (
    <div style={styles.page}>
      {/* ── Hero banner ── */}
      <div style={styles.hero}>
        <div style={styles.heroContent}>
          <div style={styles.heroLeft}>
            <div style={styles.liveChip}>
              <span style={styles.liveDot} />
              <span style={styles.liveLabel}>Live updates</span>
              {lastUpdated && <span style={styles.liveTime}>· {formatLastUpdated()}</span>}
            </div>
            <h1 style={styles.heroTitle}>Your Travel Alerts</h1>
            <p style={styles.heroSub}>
              Personalised notifications from your Europ Assistance cover team — in your language, right when it matters.
            </p>
          </div>
          <div style={styles.heroStats}>
            <div style={styles.heroStat}>
              <div style={styles.heroStatNum}>{alerts.length}</div>
              <div style={styles.heroStatLabel}>notification{alerts.length !== 1 ? 's' : ''}</div>
            </div>
            {unreadCount > 0 && (
              <div style={{ ...styles.heroStat, background: "rgba(220,38,38,0.15)", border: "1px solid rgba(220,38,38,0.35)" }}>
                <div style={{ ...styles.heroStatNum, color: "#fca5a5" }}>{unreadCount}</div>
                <div style={styles.heroStatLabel}>unread</div>
              </div>
            )}
          </div>
        </div>
        <div style={styles.heroDeco} />
      </div>

      {/* ── Carousel area ── */}
      <div style={styles.carouselWrap}>
        {alerts.length === 0 ? (
          <div style={styles.emptyState}>
            <div style={styles.emptyCircle}>
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#1d4ed8" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 9.77 19.79 19.79 0 0 1 1.61 1.14 2 2 0 0 1 3.6 0h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 7.91"/>
              </svg>
            </div>
            <h3 style={styles.emptyTitle}>All clear for now</h3>
            <p style={styles.emptySub}>No travel alerts at this time. We're monitoring your journey 24/7.</p>
          </div>
        ) : (
          <>
            <div style={styles.cardOuter}>
              <div key={animKey} style={{
                ...styles.cardAnim,
                animation: `${direction === "right" ? "fadeRight" : "fadeLeft"} 0.3s ease both`,
              }}>
                <NotificationItem
                  id={current?.id}
                  customerId={current?.customer_id}
                  message={current?.message}
                  time={current?.time}
                  isRead={current?.isRead}
                  travelType={current ? getTravelType(current) : "leisure"}
                  index={currentIndex}
                />
              </div>
            </div>

            {/* ── Nav controls ── */}
            <div style={styles.controls}>
              <button
                style={{ ...styles.navArrow, ...(currentIndex === 0 ? styles.navArrowDisabled : {}) }}
                onClick={goPrev}
                disabled={currentIndex === 0}
                aria-label="Previous notification"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="15 18 9 12 15 6"/>
                </svg>
                <span>Previous</span>
              </button>

              <div style={styles.dots}>
                {alerts.map((a, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setDirection(i > currentIndex ? "right" : "left");
                      setAnimKey(k => k + 1);
                      setCurrentIndex(i);
                    }}
                    style={{
                      ...styles.dot,
                      ...(i === currentIndex ? styles.dotActive : {}),
                      ...(i !== currentIndex && !a?.isRead ? styles.dotUnread : {}),
                    }}
                    aria-label={`Go to notification ${i + 1}`}
                  />
                ))}
              </div>

              <button
                style={{ ...styles.navArrow, ...(currentIndex === alerts.length - 1 ? styles.navArrowDisabled : {}) }}
                onClick={goNext}
                disabled={currentIndex === alerts.length - 1}
                aria-label="Next notification"
              >
                <span>Next</span>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="9 18 15 12 9 6"/>
                </svg>
              </button>
            </div>

            <div style={styles.counter}>
              <span style={styles.counterCurrent}>{currentIndex + 1}</span>
              <span style={styles.counterSep}>/</span>
              <span style={styles.counterTotal}>{alerts.length}</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

const styles = {
  page: { minHeight: "calc(100vh - 72px)", background: "#f4f6fb" },

  hero: {
    background: "linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 55%, #2563eb 100%)",
    padding: "3rem 2.5rem 2.5rem",
    position: "relative",
    overflow: "hidden",
  },
  heroContent: {
    maxWidth: "760px",
    margin: "0 auto",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-end",
    gap: "2rem",
    position: "relative",
    /* Removed zindex = 1 */
  },
  heroLeft: { flex: 1 },
  liveChip: {
    display: "inline-flex",
    alignItems: "center",
    gap: "6px",
    background: "rgba(255,255,255,0.12)",
    border: "1px solid rgba(255,255,255,0.25)",
    borderRadius: "20px",
    padding: "4px 12px",
    marginBottom: "14px",
  },
  liveDot: {
    display: "inline-block",
    width: "7px",
    height: "7px",
    borderRadius: "50%",
    background: "#DC2626",
    animation: "pulseRed 1.6s ease-in-out infinite",
  },
  liveLabel: {
    fontSize: "0.72rem",
    fontWeight: 700,
    color: "rgba(255,255,255,0.9)",
    textTransform: "uppercase",
    letterSpacing: "0.07em",
    fontFamily: "'Inter', sans-serif",
  },
  liveTime: { fontSize: "0.68rem", color: "rgba(255,255,255,0.5)" },
  heroTitle: {
    fontFamily: "'Inter', sans-serif",
    fontWeight: 800,
    fontSize: "2.2rem",
    color: "#ffffff",
    lineHeight: 1.1,
    marginBottom: "10px",
  },
  heroSub: {
    fontSize: "0.9rem",
    color: "rgba(255,255,255,0.65)",
    lineHeight: 1.6,
    maxWidth: "480px",
    fontFamily: "'Inter', sans-serif",
  },
  heroStats: {
    display: "flex",
    gap: "12px",
    flexShrink: 0,
  },
  heroStat: {
    background: "rgba(255,255,255,0.1)",
    border: "1px solid rgba(255,255,255,0.2)",
    borderRadius: "16px",
    padding: "1.25rem 1.75rem",
    textAlign: "center",
    backdropFilter: "blur(10px)",
  },
  heroStatNum: {
    fontFamily: "'Inter', sans-serif",
    fontWeight: 800,
    fontSize: "2.5rem",
    color: "#ffffff",
    lineHeight: 1,
  },
  heroStatLabel: {
    fontSize: "0.72rem",
    color: "rgba(255,255,255,0.6)",
    textTransform: "uppercase",
    letterSpacing: "0.08em",
    fontWeight: 500,
    marginTop: "4px",
    fontFamily: "'Inter', sans-serif",
  },
  heroDeco: {
    position: "absolute",
    right: "-60px",
    top: "-60px",
    width: "320px",
    height: "320px",
    borderRadius: "50%",
    background: "rgba(255,255,255,0.04)",
    pointerEvents: "none",
  },

  carouselWrap: {
    maxWidth: "680px",
    margin: "0 auto",
    padding: "2.5rem 1.5rem 3rem",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "1.5rem",
  },
  cardOuter: { width: "100%", minHeight: "160px" },
  cardAnim:  { width: "100%" },

  controls: {
    display: "flex",
    alignItems: "center",
    gap: "1.25rem",
    width: "100%",
    justifyContent: "center",
  },
  navArrow: {
    display: "flex",
    alignItems: "center",
    gap: "6px",
    background: "#ffffff",
    border: "1.5px solid #e2e8f0",
    borderRadius: "10px",
    color: "#1d4ed8",
    padding: "9px 18px",
    cursor: "pointer",
    fontSize: "0.83rem",
    fontFamily: "'Inter', sans-serif",
    fontWeight: 600,
    transition: "all 0.15s ease",
    boxShadow: "0 1px 4px rgba(0,0,0,0.06)",
  },
  navArrowDisabled: {
    color: "#cbd5e1",
    borderColor: "#f1f5f9",
    background: "#f8fafc",
    cursor: "default",
    boxShadow: "none",
  },
  dots: {
    display: "flex",
    gap: "7px",
    alignItems: "center",
    flexWrap: "wrap",
    justifyContent: "center",
    maxWidth: "260px",
  },
  dot: {
    width: "8px",
    height: "8px",
    borderRadius: "50%",
    background: "#cbd5e1",
    border: "none",
    cursor: "pointer",
    padding: 0,
    transition: "all 0.2s ease",
  },
  dotActive: { background: "#1d4ed8", width: "24px", borderRadius: "4px" },
  dotUnread: { background: "#DC2626" },

  counter: { display: "flex", gap: "4px", alignItems: "baseline" },
  counterCurrent: {
    fontFamily: "'Inter', sans-serif",
    fontWeight: 800,
    fontSize: "1.5rem",
    color: "#1d4ed8",
    lineHeight: 1,
  },
  counterSep: { color: "#94a3b8", fontSize: "1rem" },
  counterTotal: {
    fontFamily: "'Inter', sans-serif",
    fontWeight: 600,
    fontSize: "1rem",
    color: "#94a3b8",
  },

  emptyState: {
    textAlign: "center",
    padding: "4rem 2rem",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "14px",
  },
  emptyCircle: {
    width: "80px",
    height: "80px",
    borderRadius: "50%",
    background: "#EFF6FF",
    border: "2px solid #BFDBFE",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  emptyTitle: {
    fontFamily: "'Inter', sans-serif",
    fontWeight: 700,
    fontSize: "1.15rem",
    color: "#334155",
  },
  emptySub: {
    fontSize: "0.85rem",
    color: "#94a3b8",
    maxWidth: "300px",
    lineHeight: 1.6,
    fontFamily: "'Inter', sans-serif",
  },
};

export default NotificationsScreen;