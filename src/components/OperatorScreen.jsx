import { useState } from "react";

/* ─────────────────────────────────────────────────────────────────────────────
   CONSTANTS
───────────────────────────────────────────────────────────────────────────── */
const EVENT_TYPES    = ["weather_warning","flight_disruption","gov_advice_change","major_event"];
const LOCATION_TYPES = ["country","admin_area","city","airport","flight"];
const LOCATION_CODES = {
  country:    ["FR","GB"],
  admin_area: ["FR-75","FR-13","FR-06"],
  city:       ["PAR","MRS","NCE"],
  airport:    ["CDG","ORY","MRS","NCE"],
  flight:     ["BA204:2026-02-12"],
};

/* palette */
const C = {
  red:       "#DC2626",
  redLight:  "#FEF2F2",
  redBorder: "#FECACA",
  blue:      "#1d4ed8",
  blueLight: "#EFF6FF",
  blueBorder:"#BFDBFE",
  navy:      "#1e3a8a",
  slate:     "#64748b",
  border:    "#e2e8f0",
  bg:        "#f4f6fb",
  white:     "#ffffff",
};

/* ─────────────────────────────────────────────────────────────────────────────
   DONUT CHART
───────────────────────────────────────────────────────────────────────────── */
function DonutChart({ data, title, colors }) {
  const [hovered, setHovered] = useState(null);
  if (!data || !data.length) return null;
  const total = data.reduce((s, d) => s + (d.count || 0), 0);
  if (total === 0) return <p style={{ color: C.slate, fontSize:"0.8rem" }}>No data</p>;

  const SIZE = 180, CX = 90, CY = 90, R = 68, IR = 44;
  let cum = 0;

  const slices = data.map((d, i) => {
    const pct = d.count / total;
    const sa  = cum * 2 * Math.PI - Math.PI / 2;
    cum += pct;
    const ea  = cum * 2 * Math.PI - Math.PI / 2;
    return { ...d, pct, sa, ea, color: colors[i % colors.length] };
  });

  const pt = (r, a) => ({ x: CX + r * Math.cos(a), y: CY + r * Math.sin(a) });

  return (
    <div style={chartStyles.wrap}>
      {title && <div style={chartStyles.title}>{title}</div>}
      <div style={chartStyles.inner}>
        <svg width={SIZE} height={SIZE} viewBox={`0 0 ${SIZE} ${SIZE}`}>
          {slices.map((s, i) => {
            const os = pt(R, s.sa), oe = pt(R, s.ea);
            const is = pt(IR, s.sa), ie = pt(IR, s.ea);
            const la = s.pct > 0.5 ? 1 : 0;
            const path = `M ${is.x} ${is.y} L ${os.x} ${os.y} A ${R} ${R} 0 ${la} 1 ${oe.x} ${oe.y} L ${ie.x} ${ie.y} A ${IR} ${IR} 0 ${la} 0 ${is.x} ${is.y} Z`;
            return (
              <path key={i} d={path} fill={s.color}
                opacity={hovered === null || hovered === i ? 1 : 0.4}
                style={{ cursor:"pointer", transition:"all 0.18s", transform: hovered === i ? `scale(1.04)` : "scale(1)", transformOrigin:`${CX}px ${CY}px` }}
                onMouseEnter={() => setHovered(i)}
                onMouseLeave={() => setHovered(null)}
              />
            );
          })}
          {hovered !== null ? (
            <>
              <text x={CX} y={CY-8} textAnchor="middle" fill="#0f172a" fontSize="16" fontWeight="800" fontFamily="Inter,sans-serif">{slices[hovered].count}</text>
              <text x={CX} y={CY+9} textAnchor="middle" fill={slices[hovered].color} fontSize="9" fontFamily="Inter,sans-serif" fontWeight="600">{(slices[hovered].pct*100).toFixed(0)}%</text>
            </>
          ) : (
            <>
              <text x={CX} y={CY-8} textAnchor="middle" fill="#0f172a" fontSize="20" fontWeight="800" fontFamily="Inter,sans-serif">{total}</text>
              <text x={CX} y={CY+9} textAnchor="middle" fill={C.slate} fontSize="9" fontFamily="Inter,sans-serif">total</text>
            </>
          )}
        </svg>

        <div style={chartStyles.legend}>
          {slices.map((s, i) => (
            <div key={i} style={{ ...chartStyles.legendRow, opacity: hovered === null || hovered === i ? 1 : 0.4 }}
              onMouseEnter={() => setHovered(i)} onMouseLeave={() => setHovered(null)}>
              <div style={{ ...chartStyles.dot, background: s.color }} />
              <span style={chartStyles.legendLabel}>{s.category || s.label}</span>
              <span style={{ ...chartStyles.legendCount, color: s.color }}>{s.count}</span>
              <span style={chartStyles.legendPct}>{(s.pct*100).toFixed(0)}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

const chartStyles = {
  wrap:  { display:"flex", flexDirection:"column", gap:"10px", width:"100%" },
  title: { fontFamily:"'Syne',sans-serif", fontWeight:700, fontSize:"0.82rem", color:"#334155", textTransform:"uppercase", letterSpacing:"0.07em" },
  inner: { display:"flex", gap:"1.5rem", alignItems:"center", flexWrap:"wrap" },
  legend:     { display:"flex", flexDirection:"column", gap:"8px", flex:1, minWidth:"160px" },
  legendRow:  { display:"flex", alignItems:"center", gap:"8px", cursor:"pointer", transition:"opacity 0.18s" },
  dot:        { width:"9px", height:"9px", borderRadius:"50%", flexShrink:0 },
  legendLabel:{ fontSize:"0.74rem", color:"#475569", flex:1 },
  legendCount:{ fontSize:"0.8rem", fontWeight:700, fontFamily:"'Syne',sans-serif" },
  legendPct:  { fontSize:"0.68rem", color:"#94a3b8", minWidth:"28px", textAlign:"right" },
};

/* ─────────────────────────────────────────────────────────────────────────────
   SANKEY CHART
   Renders a simple top-down Sankey: Portfolio → Evaluated/Not Impacted →
   Notified (High/Moderate) / No Action (Privacy / Dup / Low Risk)
───────────────────────────────────────────────────────────────────────────── */
function SankeyChart({ simResult }) {
  const [hovered, setHovered] = useState(null);
  if (!simResult) return null;

  const {
    total_records: total = 1000,
    customers_evaluated: evaluated = 0,
    customers_not_impacted: notImpacted = 0,
    detailed_breakdown: bd = [],
  } = simResult;

  const get = (category) => (bd.find(d => d.category === category) || {}).count || 0;
  const highRisk  = get("AI Prediction: High Risk");
  const modRisk   = get("AI Prediction: Moderate Risk");
  const noConsent = get("No Consent (Privacy Block)");
  const dedup     = get("Already Contacted (Deduplicated)");
  const lowRisk   = get("No Coverage (AI Low Risk)");
  const notified  = highRisk + modRisk;
  const noAction  = noConsent + dedup + lowRisk;

  const W = 640, H = 340;
  // Column X centres
  const X0 = 60,  X1 = 220, X2 = 400, X3 = 580;
  // Node heights are proportional to their value, max 200px
  const scale = (v) => Math.max(8, (v / total) * 200);

  const nodes = [
    { id:"total",      x:X0, value:total,       color:C.navy,  label:"Portfolio", sub:`${total}` },
    { id:"evaluated",  x:X1, value:evaluated,   color:C.blue,  label:"Evaluated", sub:`${evaluated}` },
    { id:"notImpacted",x:X1, value:notImpacted, color:"#94a3b8",label:"Not Impacted",sub:`${notImpacted}` },
    { id:"notified",   x:X2, value:notified,    color:"#16a34a",label:"Notified",  sub:`${notified}` },
    { id:"noAction",   x:X2, value:noAction,    color:C.slate, label:"No Action", sub:`${noAction}` },
    { id:"highRisk",   x:X3, value:highRisk,    color:C.red,   label:"High Risk", sub:`${highRisk}` },
    { id:"modRisk",    x:X3, value:modRisk,     color:"#f59e0b",label:"Moderate", sub:`${modRisk}` },
    { id:"noConsent",  x:X3, value:noConsent,   color:"#64748b",label:"No Consent",sub:`${noConsent}` },
    { id:"dedup",      x:X3, value:dedup,       color:"#94a3b8",label:"Dedup'd",  sub:`${dedup}` },
    { id:"lowRisk",    x:X3, value:lowRisk,     color:"#cbd5e1",label:"Low Risk", sub:`${lowRisk}` },
  ];

  // Pre-compute Y centres for each node column
  const nodeH = (v) => scale(v);
  const gap   = 12;

  // Column 0
  nodes[0].h = nodeH(total); nodes[0].y = H/2 - nodes[0].h/2;

  // Column 1: two nodes stacked
  const c1Total = nodeH(evaluated) + nodeH(notImpacted) + gap;
  const c1Start = H/2 - c1Total/2;
  nodes[1].h = nodeH(evaluated);   nodes[1].y = c1Start;
  nodes[2].h = nodeH(notImpacted); nodes[2].y = c1Start + nodes[1].h + gap;

  // Column 2: notified + noAction
  const c2Total = nodeH(notified) + nodeH(noAction) + gap;
  const c2Start = H/2 - c2Total/2;
  nodes[3].h = nodeH(notified); nodes[3].y = c2Start;
  nodes[4].h = nodeH(noAction); nodes[4].y = c2Start + nodes[3].h + gap;

  // Column 3: five nodes
  const c3Hs = [highRisk, modRisk, noConsent, dedup, lowRisk].map(nodeH);
  const c3Total = c3Hs.reduce((a,b)=>a+b, 0) + gap * 4;
  let c3y = H/2 - c3Total/2;
  [5,6,7,8,9].forEach((ni, ii) => {
    nodes[ni].h = c3Hs[ii];
    nodes[ni].y = c3y;
    c3y += c3Hs[ii] + gap;
  });

  // Helper: cubic bezier flow between two nodes
  const flow = (x1, y1, h1, x2, y2, h2, color, key) => {
    if (!h1 || !h2) return null;
    const mx = (x1 + x2) / 2;
    const path = `
      M ${x1} ${y1}
      C ${mx} ${y1}, ${mx} ${y2}, ${x2} ${y2}
      L ${x2} ${y2+h2}
      C ${mx} ${y2+h2}, ${mx} ${y1+h1}, ${x1} ${y1+h1}
      Z
    `;
    const isHov = hovered === key;
    return (
      <path key={key} d={path} fill={color} opacity={isHov ? 0.55 : 0.18}
        style={{ cursor:"pointer", transition:"opacity 0.18s" }}
        onMouseEnter={() => setHovered(key)}
        onMouseLeave={() => setHovered(null)}
      />
    );
  };

  const NODE_W = 14;

  return (
    <div style={sankeyStyles.wrap}>
      <div style={sankeyStyles.title}>Decision Flow — Sankey</div>
      <div style={{ overflowX:"auto" }}>
        <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ display:"block" }}>
          {/* flows */}
          {flow(X0+NODE_W, nodes[0].y, nodes[0].h, X1-NODE_W, nodes[1].y, nodes[1].h, C.blue, "f0")}
          {flow(X0+NODE_W, nodes[0].y, nodes[0].h, X1-NODE_W, nodes[2].y, nodes[2].h, "#94a3b8", "f1")}
          {flow(X1+NODE_W, nodes[1].y, nodes[1].h, X2-NODE_W, nodes[3].y, nodes[3].h, "#16a34a", "f2")}
          {flow(X1+NODE_W, nodes[1].y, nodes[1].h, X2-NODE_W, nodes[4].y, nodes[4].h, "#64748b", "f3")}
          {flow(X2+NODE_W, nodes[3].y, nodes[3].h, X3-NODE_W, nodes[5].y, nodes[5].h, C.red,    "f4")}
          {flow(X2+NODE_W, nodes[3].y, nodes[3].h, X3-NODE_W, nodes[6].y, nodes[6].h, "#f59e0b","f5")}
          {flow(X2+NODE_W, nodes[4].y, nodes[4].h, X3-NODE_W, nodes[7].y, nodes[7].h, "#64748b","f6")}
          {flow(X2+NODE_W, nodes[4].y, nodes[4].h, X3-NODE_W, nodes[8].y, nodes[8].h, "#94a3b8","f7")}
          {flow(X2+NODE_W, nodes[4].y, nodes[4].h, X3-NODE_W, nodes[9].y, nodes[9].h, "#cbd5e1","f8")}

          {/* node bars */}
          {nodes.map((n) => (
            <g key={n.id}>
              <rect x={n.x-NODE_W/2} y={n.y} width={NODE_W} height={n.h}
                fill={n.color} rx="3"
                onMouseEnter={() => setHovered(n.id)}
                onMouseLeave={() => setHovered(null)}
                style={{ cursor:"pointer" }}
              />
              {/* label */}
              <text
                x={n.x > W/2 ? n.x + NODE_W/2 + 5 : n.x - NODE_W/2 - 5}
                y={n.y + n.h/2 + 1}
                textAnchor={n.x > W/2 ? "start" : "end"}
                fill="#334155" fontSize="9" fontFamily="Inter,sans-serif" fontWeight="600"
              >{n.label}</text>
              <text
                x={n.x > W/2 ? n.x + NODE_W/2 + 5 : n.x - NODE_W/2 - 5}
                y={n.y + n.h/2 + 12}
                textAnchor={n.x > W/2 ? "start" : "end"}
                fill={n.color} fontSize="10" fontFamily="Inter,sans-serif" fontWeight="700"
              >{n.sub}</text>
            </g>
          ))}
        </svg>
      </div>
      <div style={sankeyStyles.legend}>
        <span style={{ color: "#16a34a" }}>■</span> Notified&nbsp;&nbsp;
        <span style={{ color: C.red }}>■</span> High Risk&nbsp;&nbsp;
        <span style={{ color: "#f59e0b" }}>■</span> Moderate&nbsp;&nbsp;
        <span style={{ color: C.slate }}>■</span> No Action&nbsp;&nbsp;
        <span style={{ color: "#94a3b8" }}>■</span> Not Impacted
      </div>
    </div>
  );
}

const sankeyStyles = {
  wrap:   { display:"flex", flexDirection:"column", gap:"10px", width:"100%" },
  title:  { fontFamily:"'Syne',sans-serif", fontWeight:700, fontSize:"0.82rem", color:"#334155", textTransform:"uppercase", letterSpacing:"0.07em" },
  legend: { fontSize:"0.72rem", color:"#64748b", display:"flex", flexWrap:"wrap", gap:"4px" },
};

/* ─────────────────────────────────────────────────────────────────────────────
   STAT CARD
───────────────────────────────────────────────────────────────────────────── */
function StatCard({ label, value, color, icon }) {
  return (
    <div style={{ ...sc.card, borderColor: color + "30" }}>
      <div style={{ ...sc.icon, background: color + "12", color }}>{icon}</div>
      <div>
        <div style={{ ...sc.val, color }}>{value ?? "—"}</div>
        <div style={sc.label}>{label}</div>
      </div>
    </div>
  );
}
const sc = {
  card:  { background:C.white, border:"1.5px solid", borderRadius:"12px", padding:"14px 18px", display:"flex", alignItems:"center", gap:"12px", flex:1, minWidth:"130px" },
  icon:  { width:"36px", height:"36px", borderRadius:"9px", display:"flex", alignItems:"center", justifyContent:"center", fontSize:"1rem", flexShrink:0 },
  val:   { fontFamily:"'Syne',sans-serif", fontWeight:800, fontSize:"1.5rem", lineHeight:1 },
  label: { fontSize:"0.68rem", color:C.slate, marginTop:"3px", fontWeight:500, textTransform:"uppercase", letterSpacing:"0.06em" },
};

/* ─────────────────────────────────────────────────────────────────────────────
   FORM HELPERS
───────────────────────────────────────────────────────────────────────────── */
const sel = {
  background:C.white, border:`1.5px solid ${C.border}`, borderRadius:"8px", color:"#0f172a",
  padding:"9px 32px 9px 12px", fontSize:"0.85rem", fontFamily:"'DM Sans',sans-serif",
  cursor:"pointer", width:"100%", outline:"none", appearance:"none",
  backgroundImage:`url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2364748b' d='M6 8L1 3h10z'/%3E%3C/svg%3E")`,
  backgroundRepeat:"no-repeat", backgroundPosition:"right 10px center",
};
const inp = { ...sel, backgroundImage:"none", paddingRight:"12px" };

function Field({ label, children }) {
  return (
    <div style={{ display:"flex", flexDirection:"column", gap:"5px" }}>
      <label style={{ fontSize:"0.68rem", fontWeight:700, textTransform:"uppercase", letterSpacing:"0.08em", color:C.slate }}>{label}</label>
      {children}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────────────────
   MAIN COMPONENT
───────────────────────────────────────────────────────────────────────────── */
export default function OperatorScreen() {
  const [eventType,     setEventType]     = useState("weather_warning");
  const [eventDate,     setEventDate]     = useState("2026-02-12");
  const [locationType,  setLocationType]  = useState("airport");
  const [locationCode,  setLocationCode]  = useState("CDG");
  const [severityLevel, setSeverityLevel] = useState(4);
  const [simulateResult,setSimulateResult]= useState(null);
  const [dashboard,     setDashboard]     = useState(null);
  const [error,         setError]         = useState(null);
  const [loading,       setLoading]       = useState(false);

  const onLocationTypeChange = (t) => {
    setLocationType(t);
    setLocationCode((LOCATION_CODES[t] || [])[0] || "");
  };

  const simulateEvent = async () => {
    setError(null);
    setLoading(true);
    setDashboard(null);
    setSimulateResult(null);

    const payload = {
      event_type: eventType,
      source: "simulator",
      event_date: eventDate,
      location_type: locationType,
      location_code: locationCode,
      severity_level: Number(severityLevel),
      payload: { headline: "Simulated event (v0)" }
    };

    try {
      const res = await fetch("/api/simulate-event", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error("Simulation failed");

      const simData = await res.json();
      setSimulateResult(simData);

      // Fetch dashboard to populate Travel Purpose and Policy Tier charts
      const dashRes = await fetch(`/api/dashboard?event_id=${simData.event_id}`);
      if (!dashRes.ok) throw new Error("Dashboard fetch failed");
      setDashboard(await dashRes.json());

    } catch (err) {
      setError(err.message || "Failed to simulate event or fetch dashboard.");
    } finally {
      setLoading(false);
    }
  };
  
  /*const simulateEvent = async () => {
    setError(null); setLoading(true); setDashboard(null); setSimulateResult(null);
    const payload = { event_type:eventType, source:"simulator", event_date:eventDate, location_type:locationType, location_code:locationCode, severity_level:Number(severityLevel), payload:{ headline:"Simulated event (v0)" } };
    try {
      const res = await fetch("http://localhost:5000/simulate-event", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload) });
      if (!res.ok) throw new Error();
      const simData = await res.json();
      setSimulateResult(simData);
      const dashRes = await fetch(`http://localhost:5000/dashboard?event_id=${simData.event_id}`);
      if (!dashRes.ok) throw new Error();
      setDashboard(await dashRes.json());
    } catch { setError("Failed to simulate event or fetch dashboard."); }
    finally   { setLoading(false); }
  };*/

  const sevColors = ["","#22c55e","#84cc16","#f59e0b","#f97316",C.red];

  /* ── Derived chart datasets ── */
  const decisionPieData    = simulateResult?.detailed_breakdown || [];
  const decisionPieColors  = [C.red,"#f59e0b","#64748b","#94a3b8","#cbd5e1"];

  
  const evaluated = simulateResult?.customers_evaluated || 0;
  const purposeData = dashboard?.purpose_breakdown || [];
  const purposeColors = [C.blue, C.red];

  
  const notified   = (simulateResult?.notifications_created || 0);
  const policyData = dashboard?.policy_breakdown || [];
  const policyColors = ["#94a3b8", C.blue, C.red];

  return (
    <div style={S.page}>
      <style>{`select option { background:#fff; color:#0f172a; }`}</style>

      <div style={S.layout}>

        {/* ── SIDEBAR ── */}
        <aside style={S.sidebar}>
          <div style={S.sideHeader}>
            <div style={S.sideIcon}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={C.blue} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
              </svg>
            </div>
            <div>
              <div style={S.sideTitle}>Event Simulator</div>
              <div style={S.sideSub}>Trigger an event & assess impact</div>
            </div>
          </div>

          <div style={S.fields}>
            <Field label="Event Type">
              <select style={sel} value={eventType} onChange={e=>setEventType(e.target.value)}>
                {EVENT_TYPES.map(t=><option key={t} value={t}>{t.replace(/_/g," ")}</option>)}
              </select>
            </Field>

            <Field label="Event Date">
              <input type="date" style={inp} value={eventDate} onChange={e=>setEventDate(e.target.value)}/>
            </Field>

            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"10px" }}>
              <Field label="Location Type">
                <select style={sel} value={locationType} onChange={e=>onLocationTypeChange(e.target.value)}>
                  {LOCATION_TYPES.map(t=><option key={t} value={t}>{t}</option>)}
                </select>
              </Field>
              <Field label="Location Code">
                <select style={sel} value={locationCode} onChange={e=>setLocationCode(e.target.value)}>
                  {(LOCATION_CODES[locationType]||[]).map(c=><option key={c} value={c}>{c}</option>)}
                </select>
              </Field>
            </div>

            <Field label={`Severity — ${severityLevel} / 5`}>
              <div style={{ display:"flex", gap:"6px" }}>
                {[1,2,3,4,5].map(n=>(
                  <button key={n} onClick={()=>setSeverityLevel(n)} style={{
                    flex:1, padding:"9px 0", borderRadius:"8px", cursor:"pointer",
                    fontSize:"0.88rem", fontWeight:700, fontFamily:"'Syne',sans-serif",
                    transition:"all 0.15s",
                    background: n<=severityLevel ? sevColors[n] : "#f8fafc",
                    border: `1.5px solid ${n<=severityLevel ? sevColors[n]+"90" : C.border}`,
                    color: n<=severityLevel ? "#fff" : "#94a3b8",
                  }}>{n}</button>
                ))}
              </div>
            </Field>
          </div>

          <button onClick={simulateEvent} disabled={loading||!locationCode} style={{
            ...S.runBtn,
            opacity: loading||!locationCode ? 0.55 : 1,
            cursor:  loading||!locationCode ? "default" : "pointer",
          }}>
            {loading
              ? <><span style={S.spinner}/>Running…</>
              : <><svg width="14" height="14" viewBox="0 0 24 24" fill="white" stroke="none"><polygon points="5 3 19 12 5 21 5 3"/></svg>Simulate Event</>
            }
          </button>

          <button
            onClick={async () => {
              try {
                const res = await fetch("/api/admin/reset", {
                  method: "POST"
                });

                if (!res.ok) throw new Error();
                alert("Reset OK");
              } catch {
                alert("Reset failed");
              }
            }}
          >
            Reset Demo
          </button>

          {error && (
            <div style={S.errorBox}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={C.red} strokeWidth="2.2" strokeLinecap="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              {error}
            </div>
          )}
        </aside>

        {/* ── RESULTS ── */}
        <section style={S.results}>
          {!simulateResult && !loading && (
            <div style={S.empty}>
              <div style={S.emptyIcon}>
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke={C.blue} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                </svg>
              </div>
              <h3 style={S.emptyTitle}>No simulation run yet</h3>
              <p style={S.emptySub}>Configure an event and click Simulate to see results, charts, and flow analysis.</p>
            </div>
          )}

          {simulateResult && (<>

            {/* Result banner */}
            <div style={S.resultBanner}>
              <div>
                <div style={S.resultTitle}>Simulation Complete</div>
                <div style={S.resultSub}>Event ID: <code style={S.code}>{simulateResult.event_id}</code></div>
              </div>
              <div style={S.doneBadge}>✓ Done</div>
            </div>

            {/* Stat cards */}
            <div style={S.statsRow}>
              <StatCard label="Portfolio"    value={simulateResult.total_records}          color={C.navy}      icon="🗂"/>
              <StatCard label="Evaluated"    value={simulateResult.customers_evaluated}    color={C.blue}      icon="👥"/>
              <StatCard label="Notified"     value={simulateResult.notifications_created}  color="#16a34a"     icon="📨"/>
              <StatCard label="Not Impacted" value={simulateResult.customers_not_impacted} color={C.slate}     icon="🛡"/>
            </div>

            {/* Sankey */}
            <div style={S.card}>
              <SankeyChart simResult={simulateResult}/>
            </div>

            {/* Pie charts row */}
            <div style={S.chartsRow}>
              <div style={S.card}>
                <DonutChart
                  data={decisionPieData}
                  title="Decision Breakdown"
                  colors={decisionPieColors}
                />
              </div>
              <div style={S.card}>
                <DonutChart
                  data={purposeData}
                  title="Travel Purpose"
                  colors={purposeColors}
                />
              </div>
              <div style={S.card}>
                <DonutChart
                  data={policyData}
                  title="Policy Tier"
                  colors={policyColors}
                />
              </div>
            </div>

            {/* Dashboard (if loaded) */}
            {dashboard && (
              <div style={S.card}>
                <div style={{ ...sankeyStyles.title, marginBottom:"12px" }}>
                  Dashboard — Event <code style={S.code}>#{dashboard.event_id}</code>
                </div>
              
                <details style={S.rawDetails}>
                  <summary style={S.rawSum}>View raw JSON</summary>
                  <pre style={S.rawPre}>{JSON.stringify(dashboard, null, 2)}</pre>
                </details>
              </div>
            )}

          </>)}
        </section>
      </div>
    </div>
  );
}

const S = {
  page:   { minHeight:"calc(100vh - 68px)", background:C.bg, padding:"2rem" },
  layout: { maxWidth:"1160px", margin:"0 auto", display:"grid", gridTemplateColumns:"320px 1fr", gap:"1.5rem", alignItems:"start" },

  sidebar:    { background:C.white, border:`1.5px solid ${C.border}`, borderRadius:"16px", padding:"1.75rem", display:"flex", flexDirection:"column", gap:"1.4rem", position:"sticky", top:"84px", boxShadow:"0 2px 12px rgba(0,0,0,0.05)" },
  sideHeader: { display:"flex", alignItems:"center", gap:"12px" },
  sideIcon:   { width:"40px", height:"40px", borderRadius:"10px", background:C.blueLight, border:`1px solid ${C.blueBorder}`, display:"flex", alignItems:"center", justifyContent:"center", flexShrink:0 },
  sideTitle:  { fontFamily:"'Syne',sans-serif", fontWeight:700, fontSize:"1rem", color:"#0f172a" },
  sideSub:    { fontSize:"0.72rem", color:C.slate, marginTop:"2px" },
  fields:     { display:"flex", flexDirection:"column", gap:"1rem" },

  runBtn: {
    display:"flex", alignItems:"center", justifyContent:"center", gap:"8px",
    background:`linear-gradient(135deg, ${C.navy} 0%, ${C.blue} 100%)`,
    border:"none", borderRadius:"10px", color:"#fff",
    padding:"12px", fontSize:"0.9rem", fontFamily:"'Syne',sans-serif", fontWeight:700,
    transition:"all 0.2s", boxShadow:"0 4px 16px rgba(29,78,216,0.3)", letterSpacing:"0.02em",
  },
  spinner: {
    display:"inline-block", width:"13px", height:"13px",
    border:"2px solid rgba(255,255,255,0.3)", borderTopColor:"#fff",
    borderRadius:"50%", animation:"spin 0.8s linear infinite",
  },
  errorBox: {
    background:C.redLight, border:`1px solid ${C.redBorder}`, borderRadius:"8px",
    padding:"10px 14px", fontSize:"0.8rem", color:C.red, display:"flex", gap:"8px", alignItems:"center",
  },

  results:   { display:"flex", flexDirection:"column", gap:"1.25rem" },
  card:      { background:C.white, border:`1.5px solid ${C.border}`, borderRadius:"14px", padding:"1.5rem", boxShadow:"0 1px 6px rgba(0,0,0,0.04)" },
  chartsRow: { display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:"1rem" },

  empty:      { background:C.white, border:`1.5px dashed ${C.border}`, borderRadius:"14px", padding:"4rem 2rem", textAlign:"center", display:"flex", flexDirection:"column", alignItems:"center", gap:"12px" },
  emptyIcon:  { width:"72px", height:"72px", borderRadius:"50%", background:C.blueLight, border:`1.5px solid ${C.blueBorder}`, display:"flex", alignItems:"center", justifyContent:"center" },
  emptyTitle: { fontFamily:"'Syne',sans-serif", fontWeight:700, fontSize:"1.1rem", color:"#334155" },
  emptySub:   { fontSize:"0.82rem", color:"#94a3b8", maxWidth:"300px", lineHeight:1.6 },

  resultBanner: { background:`linear-gradient(135deg, ${C.navy}, ${C.blue})`, borderRadius:"14px", padding:"1.25rem 1.5rem", display:"flex", justifyContent:"space-between", alignItems:"center", color:"#fff" },
  resultTitle:  { fontFamily:"'Syne',sans-serif", fontWeight:700, fontSize:"1.05rem" },
  resultSub:    { fontSize:"0.78rem", color:"rgba(255,255,255,0.65)", marginTop:"3px" },
  doneBadge:    { background:"rgba(255,255,255,0.15)", border:"1px solid rgba(255,255,255,0.3)", borderRadius:"20px", padding:"4px 14px", fontSize:"0.78rem", fontWeight:600 },

  statsRow: { display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:"10px" },

  code:       { background:C.blueLight, color:C.blue, padding:"1px 6px", borderRadius:"4px", fontSize:"0.85em", fontFamily:"monospace" },
  rawDetails: { borderTop:`1px solid ${C.border}`, paddingTop:"12px", marginTop:"12px" },
  rawSum:     { fontSize:"0.75rem", color:"#94a3b8", cursor:"pointer", fontWeight:500 },
  rawPre:     { background:"#f8fafc", borderRadius:"8px", padding:"12px", fontSize:"0.7rem", color:C.slate, marginTop:"10px", overflowX:"auto", lineHeight:1.5, fontFamily:"monospace" },
};