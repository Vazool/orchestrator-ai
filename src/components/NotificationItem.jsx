import { useState } from "react";

/* ─── Feedback Dialog ─────────────────────────────────────────────────────── */
function FeedbackDialog({ onClose, onSelect }) {
  const emojis = [
    { icon: "😢", label: "Unhappy",  mood: "sad" },
    { icon: "😐", label: "Neutral",  mood: "neutral" },
    { icon: "😄", label: "Happy",    mood: "happy" },
  ];
  const [hovered, setHovered] = useState(null);

  return (
    <div style={dlg.overlay} onClick={onClose}>
      <div style={dlg.modal} onClick={e => e.stopPropagation()}>
        <button style={dlg.closeBtn} onClick={onClose} aria-label="Close">✕</button>

        {/* Header */}
        <div style={dlg.header}>
          <div style={dlg.headerIcon}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1d4ed8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
            </svg>
          </div>
          <div>
            <h3 style={dlg.title}>How do you feel about this support service?</h3>
            <p style={dlg.subtitle}>Would you like more assistance?</p>
          </div>
        </div>

        {/* Emoji row */}
        <div style={dlg.emojiRow}>
          {emojis.map((e, i) => (
            <button
              key={i}
              style={{
                ...dlg.emojiBtn,
                ...(hovered === i ? dlg.emojiBtnHover : {}),
              }}
              onMouseEnter={() => setHovered(i)}
              onMouseLeave={() => setHovered(null)}
              onClick={() => onSelect(e.mood)}
              aria-label={e.label}
            >
              <span style={dlg.emojiIcon}>{e.icon}</span>
              <span style={dlg.emojiLabel}>{e.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ─── Assistance Screen ───────────────────────────────────────────────────── */
function AssistanceScreen({ onClose }) {
  return (
    <div style={dlg.overlay} onClick={onClose}>
      <div style={{ ...dlg.modal, maxWidth: "460px" }} onClick={e => e.stopPropagation()}>
        <button style={dlg.closeBtn} onClick={onClose} aria-label="Close">✕</button>

        <div style={dlg.header}>
          <div style={{ ...dlg.headerIcon, background: "#FEF2F2", border: "1.5px solid #FECACA" }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#DC2626" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 9.77 19.79 19.79 0 0 1 1.61 1.14 2 2 0 0 1 3.6 0h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 7.91"/>
            </svg>
          </div>
          <div>
            <h3 style={{ ...dlg.title, color: "#DC2626" }}>We're Here to Help You</h3>
            <p style={dlg.subtitle}>Urgent assistance available 24/7</p>
          </div>
        </div>

        <div style={assist.phoneCard}>
          <div style={assist.phoneIcon}>📞</div>
          <div>
            <div style={assist.phoneLabel}>Urgent Assistance Line</div>
            <div style={assist.phoneNumber}>+33 1 41 85 85 85</div>
          </div>
        </div>

        <div style={assist.services}>
          <div style={assist.servicesTitle}>We can help you with:</div>
          <div style={assist.serviceGrid}>
            {[
              { icon: "🏨", text: "Book a hotel" },
              { icon: "✈️", text: "Rebook your flight" },
              { icon: "🚗", text: "Arrange transport" },
              { icon: "🏥", text: "Medical assistance" },
              { icon: "📋", text: "Insurance claims" },
              { icon: "🔐", text: "Lost documents" },
            ].map((s, i) => (
              <div key={i} style={assist.serviceItem}>
                <span style={assist.serviceEmoji}>{s.icon}</span>
                <span style={assist.serviceText}>{s.text}</span>
              </div>
            ))}
          </div>
        </div>

        <button style={assist.callBtn} onClick={() => window.open("tel:+33141858585")}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 9.77 19.79 19.79 0 0 1 1.61 1.14 2 2 0 0 1 3.6 0h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 7.91"/>
          </svg>
          Call Now — Free of Charge
        </button>
      </div>
    </div>
  );
}

/* ─── Happy Screen ────────────────────────────────────────────────────────── */
function HappyScreen({ onClose }) {
  return (
    <div style={dlg.overlay} onClick={onClose}>
      <div style={{ ...dlg.modal, maxWidth: "360px", textAlign: "center" }} onClick={e => e.stopPropagation()}>
        <button style={dlg.closeBtn} onClick={onClose} aria-label="Close">✕</button>
        <div style={happy.emoji}>😊</div>
        <h3 style={happy.title}>Glad we could help!</h3>
        <p style={happy.sub}>
          Your safety and comfort are our top priority. We're monitoring your journey 24/7.
        </p>
        <button style={happy.btn} onClick={onClose}>Thank you</button>
      </div>
    </div>
  );
}

/* ─── Why Dialog ──────────────────────────────────────────────────────────── */
function WhyDialog({ onClose, onOptOut, optedOut }) {
  return (
    <div style={dlg.overlay} onClick={onClose}>
      <div style={{ ...dlg.modal, maxWidth: "460px" }} onClick={e => e.stopPropagation()}>
        <button style={dlg.closeBtn} onClick={onClose} aria-label="Close">✕</button>

        <div style={dlg.header}>
          <div style={{ ...dlg.headerIcon, background: "#F0FDF4", border: "1.5px solid #BBF7D0" }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#15803d" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <div>
            <h3 style={dlg.title}>Why are you seeing this?</h3>
            <p style={dlg.subtitle}>Your notification preferences explained</p>
          </div>
        </div>

        <div style={why.body}>
          <p style={why.para}>
            You're receiving these travel alerts because you <strong>opted in</strong> to proactive notifications when you purchased your Europ Assistance travel insurance policy.
          </p>

          <div style={why.infoGrid}>
            {[
              { icon: "🛡", title: "Your policy cover", text: "Alerts are matched to your specific policy tier and destination." },
              { icon: "📍", title: "Location-based", text: "We monitor events near your destination in real time." },
              { icon: "🌐", title: "Your language", text: "Messages are personalised and sent in your preferred language." },
              { icon: "🔒", title: "GDPR compliant", text: "Your data is handled under the Brussels Privacy Protocol. We never share your PII with third-party AI providers." },
            ].map((item, i) => (
              <div key={i} style={why.infoItem}>
                <span style={why.infoIcon}>{item.icon}</span>
                <div>
                  <div style={why.infoTitle}>{item.title}</div>
                  <div style={why.infoText}>{item.text}</div>
                </div>
              </div>
            ))}
          </div>

          {optedOut ? (
            <div style={why.optedOutBanner}>
              ✓ You have successfully opted out. You will no longer receive travel alerts.
            </div>
          ) : (
            <p style={why.smallPrint}>
              You can withdraw your consent at any time. Opting out will prevent future notifications but does not affect your insurance cover.
            </p>
          )}
        </div>

        <div style={why.footer}>
          {!optedOut && (
            <button style={why.optOutBtn} onClick={onOptOut}>
              Opt Out
            </button>
          )}
          <button style={why.closeBtn} onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}


function NotificationItem({ id: alertId, customerId, message, time, isRead: initialRead, travelType, index = 0, onMarkRead }) {
  const [isRead, setIsRead] = useState(initialRead);
  const [dialog, setDialog] = useState(null); // null | "feedback" | "assist" | "happy" | "why"
  const [optedOut, setOptedOut] = useState(false);

  const handleCardClick = () => {
    // Clicking the card body only marks it as read — does NOT open feedback
    if (!isRead) {
      setIsRead(true);
      if (onMarkRead) onMarkRead();
      if (alertId) {
        fetch(`/api/alerts/${alertId}/read`, { method: "PATCH" })
          .catch(err => console.error("Mark-read failed:", err));
      }
    }
  };

  const handleFeedbackClick = (e) => {
    e.stopPropagation();
    setDialog("feedback");
  };

  const handleWhyClick = (e) => {
    e.stopPropagation();
    setDialog("why");
  };

  const handleOptOut = () => {
    if (!customerId) return;
    fetch(`/api/customers/${customerId}/opt-out`, { method: "PATCH" })
      .then(() => setOptedOut(true))
      .catch(err => console.error("Opt-out failed:", err));
  };

  const handleEmojiSelect = (mood) => {
    setDialog(null);
    // Persist emoji feedback to backend
    if (alertId) {
      fetch("/api/alerts/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ alert_id: alertId, mood }),
      }).catch(err => console.error("Feedback save failed:", err));
    }
    if (mood === "sad" || mood === "neutral") {
      setDialog("assist");
    } else {
      setDialog("happy");
    }
  };

  const isRTL = /[\u0600-\u06FF\u0590-\u05FF]/.test(message);

  const formatTime = (t) => {
    if (!t) return "";
    try {
      const d = new Date(t);
      if (isNaN(d)) return t;
      return d.toLocaleString(undefined, {
        day: "numeric", month: "short",
        hour: "2-digit", minute: "2-digit",
      });
    } catch { return t; }
  };

  

  const travelConfig = travelType === "business"
    ? { icon: "💼", label: "Business", bg: "#F0FDF4", border: "#BBF7D0", color: "#15803d" }
    : { icon: "🏖️", label: "Leisure",  bg: "#FFF7ED", border: "#FED7AA", color: "#c2410c" };

  return (
    <>
      <div
        style={{
          ...styles.card,
          ...(isRead ? styles.cardRead : styles.cardUnread),
        }}
        onClick={handleCardClick}
      >
        {/* Left accent bar */}
        <div style={{
          ...styles.accentBar,
          background: isRead
            ? "linear-gradient(180deg, #cbd5e1, #e2e8f0)"
            : "linear-gradient(180deg, #DC2626, #1d4ed8)",
        }} />

        <div style={styles.inner}>
          {/* Top meta row */}
          <div style={styles.metaRow}>
            <div style={styles.metaLeft}>
              {/* Travel type tag */}
              <span style={{
                ...styles.travelChip,
                background: travelConfig.bg,
                border: `1px solid ${travelConfig.border}`,
                color: travelConfig.color,
              }}>
                {travelConfig.icon}&nbsp;{travelConfig.label}
              </span>

              {!isRead && <span style={styles.newBadge}>● New</span>}
              {isRead && (
                <span style={styles.readIcon} title="Message read">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#22c55e" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                  Read
                </span>
              )}
            </div>
            {time && (
              <div style={styles.timeRow}>
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                </svg>
                <span style={styles.time}>{formatTime(time)}</span>
              </div>
            )}
          </div>

          {/* Message body */}
          <p style={{
            ...styles.message,
            direction: isRTL ? "rtl" : "ltr",
            textAlign: isRTL ? "right" : "left",
            color: isRead ? "#64748b" : "#1e293b",
          }}>
            {message}
          </p>

          {/* Bottom footer */}
          <div style={styles.footer}>
            <div style={styles.footerLeft}>
              <div style={styles.eaLogo}>
                <svg width="14" height="14" viewBox="0 0 38 38" fill="none">
                  <rect width="38" height="38" rx="5" fill="#DC2626"/>
                  <circle cx="19" cy="19" r="8.5" stroke="white" strokeWidth="2.2"/>
                  <path d="M10.5 19h17M19 10.5v17" stroke="white" strokeWidth="2.2" strokeLinecap="round"/>
                </svg>
              </div>
              <button
              onClick={handleWhyClick}
              style={styles.whyBtn}
              aria-label="Why am I seeing this?"
            >
              Why am I seeing this?
            </button>
            </div>
            
            <button
              onClick={handleFeedbackClick}
              style={styles.feedbackBtn}
              aria-label="Give feedback"
            >
              Click here to respond →
            </button>
          </div>
        </div>
      </div>

      {dialog === "feedback"  && <FeedbackDialog onClose={() => setDialog(null)} onSelect={handleEmojiSelect} />}
      {dialog === "assist"    && <AssistanceScreen onClose={() => setDialog(null)} />}
      {dialog === "happy"     && <HappyScreen onClose={() => setDialog(null)} />}
      {dialog === "why"       && <WhyDialog onClose={() => setDialog(null)} onOptOut={handleOptOut} optedOut={optedOut} />}
    </>
  );
}

/* ─── Styles ──────────────────────────────────────────────────────────────── */
const styles = {
  card: {
    borderRadius: "16px",
    display: "flex",
    overflow: "hidden",
    boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
    transition: "box-shadow 0.2s ease, transform 0.15s ease",
    width: "100%",
  },
  cardUnread: {
    background: "#ffffff",
    border: "1.5px solid #BFDBFE",
    boxShadow: "0 6px 28px rgba(29,78,216,0.1)",
  },
  cardRead: {
    background: "#f8fafc",
    border: "1.5px solid #e2e8f0",
    boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
  },
  accentBar: { width: "4px", flexShrink: 0 },
  inner: {
    padding: "18px 22px",
    flex: 1,
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  metaRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "8px",
    flexWrap: "wrap",
  },
  metaLeft: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    flexWrap: "wrap",
  },
  langChip: {
    fontSize: "0.7rem",
    fontWeight: 700,
    padding: "3px 9px",
    borderRadius: "20px",
    letterSpacing: "0.05em",
    fontFamily: "'Inter', sans-serif",
  },
  travelChip: {
    fontSize: "0.7rem",
    fontWeight: 600,
    padding: "3px 9px",
    borderRadius: "20px",
    letterSpacing: "0.03em",
    fontFamily: "'Inter', sans-serif",
  },
  newBadge: {
    fontSize: "0.68rem",
    fontWeight: 700,
    color: "#DC2626",
    letterSpacing: "0.04em",
    fontFamily: "'Inter', sans-serif",
  },
  readIcon: {
    display: "flex",
    alignItems: "center",
    gap: "4px",
    fontSize: "0.68rem",
    fontWeight: 600,
    color: "#22c55e",
    animation: "fadeIn 0.3s ease",
  },
  timeRow: { display: "flex", alignItems: "center", gap: "4px" },
  time: {
    fontSize: "0.72rem",
    color: "#94a3b8",
    fontVariantNumeric: "tabular-nums",
  },
  message: {
    fontSize: "0.95rem",
    lineHeight: 1.7,
    fontFamily: "'Inter', sans-serif",
    fontWeight: 400,
  },
  footer: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    paddingTop: "10px",
    borderTop: "1px solid #f1f5f9",
  },
  footerLeft: { display: "flex", alignItems: "center", gap: "7px" },
  eaLogo: { flexShrink: 0 },
  
  whyBtn: {
    fontSize: "0.68rem",
    fontWeight: 600,
    color: "#64748b",
    background: "transparent",
    border: "1px solid #e2e8f0",
    borderRadius: "8px",
    padding: "4px 10px",
    cursor: "pointer",
    fontFamily: "'Inter', sans-serif",
  },
    feedbackBtn: {fontSize: "0.68rem",
    fontWeight: 600,
    color: "#1d4ed8",
    background: "#EFF6FF",
    border: "1px solid #BFDBFE",
    borderRadius: "8px",
    padding: "4px 10px",
    cursor: "pointer",
    fontFamily: "'Inter', sans-serif",
    transition: "background 0.15s ease",
  },
};

/* ─── Dialog Styles ───────────────────────────────────────────────────────── */
const dlg = {
  overlay: {
    position: "fixed",
    inset: 0,
    background: "rgba(15,23,42,0.55)",
    backdropFilter: "blur(4px)",
    zIndex: 1000,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "1rem",
  },
  modal: {
    background: "#ffffff",
    borderRadius: "20px",
    padding: "2rem",
    maxWidth: "520px",
    width: "100%",
    boxShadow: "0 25px 60px rgba(0,0,0,0.18)",
    animation: "fadeIn 0.25s ease",
    position: "relative",
  },
  closeBtn: {
    position: "absolute",
    top: "14px",
    right: "16px",
    background: "#f1f5f9",
    border: "none",
    borderRadius: "50%",
    width: "28px",
    height: "28px",
    cursor: "pointer",
    fontSize: "0.75rem",
    color: "#64748b",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: 700,
  },
  header: {
    display: "flex",
    alignItems: "flex-start",
    gap: "14px",
    marginBottom: "1.75rem",
  },
  headerIcon: {
    width: "48px",
    height: "48px",
    borderRadius: "12px",
    background: "#EFF6FF",
    border: "1.5px solid #BFDBFE",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  },
  title: {
    fontFamily: "'Inter', sans-serif",
    fontWeight: 700,
    fontSize: "1.05rem",
    color: "#0f172a",
    lineHeight: 1.3,
  },
  subtitle: {
    fontSize: "0.82rem",
    color: "#64748b",
    marginTop: "4px",
  },
  emojiRow: {
    display: "flex",
    gap: "10px",
    justifyContent: "space-between",
  },
  emojiBtn: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "8px",
    background: "#f8fafc",
    border: "1.5px solid #e2e8f0",
    borderRadius: "14px",
    padding: "16px 8px",
    cursor: "pointer",
    transition: "all 0.18s ease",
    fontFamily: "'Inter', sans-serif",
  },
  emojiBtnHover: {
    background: "#EFF6FF",
    border: "1.5px solid #BFDBFE",
    transform: "translateY(-3px)",
    boxShadow: "0 6px 20px rgba(29,78,216,0.12)",
  },
  emojiIcon: { fontSize: "2rem", lineHeight: 1 },
  emojiLabel: { fontSize: "0.65rem", fontWeight: 600, color: "#64748b", textAlign: "center" },
};

/* ─── Assistance Styles ───────────────────────────────────────────────────── */
const assist = {
  phoneCard: {
    display: "flex",
    alignItems: "center",
    gap: "14px",
    background: "#FEF2F2",
    border: "1.5px solid #FECACA",
    borderRadius: "12px",
    padding: "16px 18px",
    marginBottom: "1.25rem",
  },
  phoneIcon: { fontSize: "1.75rem", lineHeight: 1 },
  phoneLabel: {
    fontSize: "0.72rem",
    fontWeight: 600,
    color: "#DC2626",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
    fontFamily: "'Inter', sans-serif",
  },
  phoneNumber: {
    fontFamily: "'Inter', sans-serif",
    fontWeight: 800,
    fontSize: "1.4rem",
    color: "#0f172a",
    letterSpacing: "-0.01em",
  },
  services: { marginBottom: "1.5rem" },
  servicesTitle: {
    fontSize: "0.8rem",
    fontWeight: 600,
    color: "#475569",
    marginBottom: "10px",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
    fontFamily: "'Inter', sans-serif",
  },
  serviceGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    gap: "8px",
  },
  serviceItem: {
    display: "flex",
    alignItems: "center",
    gap: "7px",
    background: "#f8fafc",
    border: "1px solid #e2e8f0",
    borderRadius: "8px",
    padding: "8px 10px",
  },
  serviceEmoji: { fontSize: "1rem" },
  serviceText: { fontSize: "0.72rem", fontWeight: 500, color: "#475569", fontFamily: "'Inter', sans-serif" },
  callBtn: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
    width: "100%",
    background: "linear-gradient(135deg, #DC2626, #b91c1c)",
    color: "#fff",
    border: "none",
    borderRadius: "12px",
    padding: "14px",
    fontSize: "0.92rem",
    fontWeight: 700,
    fontFamily: "'Inter', sans-serif",
    cursor: "pointer",
    boxShadow: "0 4px 18px rgba(220,38,38,0.3)",
    letterSpacing: "0.01em",
  },
};

/* ─── Happy Styles ────────────────────────────────────────────────────────── */
const happy = {
  emoji: { fontSize: "4rem", textAlign: "center", marginBottom: "0.75rem", animation: "fadeIn 0.3s ease" },
  title: {
    fontFamily: "'Inter', sans-serif",
    fontWeight: 700,
    fontSize: "1.3rem",
    color: "#0f172a",
    marginBottom: "10px",
  },
  sub: {
    fontSize: "0.88rem",
    color: "#64748b",
    lineHeight: 1.6,
    marginBottom: "1.5rem",
  },
  btn: {
    width: "100%",
    background: "linear-gradient(135deg, #1e3a8a, #1d4ed8)",
    color: "#fff",
    border: "none",
    borderRadius: "12px",
    padding: "13px",
    fontSize: "0.9rem",
    fontWeight: 700,
    fontFamily: "'Inter', sans-serif",
    cursor: "pointer",
    boxShadow: "0 4px 18px rgba(29,78,216,0.25)",
  },
};

/* ─── Why Styles ──────────────────────────────────────────────────────────── */
const why = {
  body: { display: "flex", flexDirection: "column", gap: "16px", marginBottom: "1.5rem" },
  para: { fontSize: "0.88rem", color: "#334155", lineHeight: 1.7, fontFamily: "'Inter', sans-serif" },
  infoGrid: { display: "flex", flexDirection: "column", gap: "10px" },
  infoItem: {
    display: "flex", alignItems: "flex-start", gap: "12px",
    background: "#f8fafc", border: "1px solid #e2e8f0",
    borderRadius: "10px", padding: "12px 14px",
  },
  infoIcon: { fontSize: "1.2rem", lineHeight: 1, flexShrink: 0, marginTop: "1px" },
  infoTitle: { fontSize: "0.78rem", fontWeight: 700, color: "#1e293b", fontFamily: "'Inter', sans-serif", marginBottom: "2px" },
  infoText:  { fontSize: "0.74rem", color: "#64748b", lineHeight: 1.5, fontFamily: "'Inter', sans-serif" },
  smallPrint: { fontSize: "0.74rem", color: "#94a3b8", lineHeight: 1.6, fontFamily: "'Inter', sans-serif" },
  optedOutBanner: {
    background: "#F0FDF4", border: "1px solid #BBF7D0", borderRadius: "10px",
    padding: "12px 16px", fontSize: "0.82rem", fontWeight: 600,
    color: "#15803d", fontFamily: "'Inter', sans-serif",
  },
  footer: { display: "flex", gap: "10px", justifyContent: "flex-end" },
  optOutBtn: {
    background: "#FEF2F2", border: "1.5px solid #FECACA", borderRadius: "10px",
    color: "#DC2626", padding: "10px 20px", fontSize: "0.85rem",
    fontWeight: 700, fontFamily: "'Inter', sans-serif", cursor: "pointer",
  },
  closeBtn: {
    background: "linear-gradient(135deg, #1e3a8a, #1d4ed8)", border: "none",
    borderRadius: "10px", color: "#fff", padding: "10px 24px",
    fontSize: "0.85rem", fontWeight: 700, fontFamily: "'Inter', sans-serif",
    cursor: "pointer", boxShadow: "0 4px 14px rgba(29,78,216,0.25)",
  },
};

export default NotificationItem;