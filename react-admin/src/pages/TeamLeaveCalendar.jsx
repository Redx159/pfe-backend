import { useEffect, useMemo, useState } from "react";
import { fetchLeaves } from "../api/leavesApi";
import { useAppShell } from "../context/AppShellContext";
import Navbar from "./components/Navbar";

const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const STATUS_COLORS = {
  APPROVED: "#1a7f37",
  PENDING: "#9a6700",
};

export default function TeamLeaveCalendar() {
  const { t } = useAppShell();
  const [leaves, setLeaves] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("APPROVED");
  const [year, setYear] = useState(new Date().getFullYear());
  const [month, setMonth] = useState(new Date().getMonth());

  useEffect(() => {
    fetchLeaves()
      .then((res) => setLeaves(res.data))
      .finally(() => setLoading(false));
  }, []);

  const filtered = filter === "ALL"
    ? leaves.filter((l) => l.status !== "REJECTED" && l.status !== "CANCELLED")
    : leaves.filter((l) => l.status === filter);

  const dateToLeaves = useMemo(() => {
    const map = {};
    for (const lv of filtered) {
      const start = new Date(lv.start_date + "T00:00:00");
      const end = new Date(lv.end_date + "T00:00:00");
      let d = new Date(start);
      while (d <= end) {
        const key = `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
        if (!map[key]) map[key] = [];
        map[key].push(lv);
        const next = new Date(d);
        next.setDate(next.getDate() + 1);
        d = next;
      }
    }
    return map;
  }, [filtered]);

  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const firstDayOfWeek = new Date(year, month, 1).getDay();
  const weeks = [];
  let cells = [];
  for (let i = 0; i < firstDayOfWeek; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) {
    cells.push(d);
    if (cells.length === 7) { weeks.push(cells); cells = []; }
  }
  if (cells.length > 0) weeks.push(cells);

  const prevMonth = () => { if (month === 0) { setYear(y => y - 1); setMonth(11); } else setMonth(m => m - 1); };
  const nextMonth = () => { if (month === 11) { setYear(y => y + 1); setMonth(0); } else setMonth(m => m + 1); };
  const today = new Date();

  if (loading) {
    return <><Navbar /><div style={{ padding: 20 }}>{t("common.loading")}</div></>;
  }

  return (
    <>
      <Navbar />
      <div style={{ padding: 20, background: "var(--bg)", minHeight: "100vh" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, marginBottom: 22 }}>
          <div>
            <h1 style={{ marginBottom: 6 }}>{t("teamLeaveCalendar.title")}</h1>
            <p style={{ margin: 0, color: "var(--muted)" }}>{t("teamLeaveCalendar.subtitle")}</p>
          </div>
          <select value={filter} onChange={(e) => setFilter(e.target.value)} style={{ width: 150 }}>
            <option value="ALL">{t("leaves.all")}</option>
            <option value="APPROVED">{t("common.approved")}</option>
            <option value="PENDING">{t("common.pending")}</option>
          </select>
        </div>

        <div style={{
          border: "1px solid var(--border)", borderRadius: 14, padding: 18,
          background: "var(--surface)", maxWidth: 1000,
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
            <button onClick={prevMonth} style={{ padding: "6px 14px" }}>&larr; Prev</button>
            <h2 style={{ margin: 0 }}>{MONTHS[month]} {year}</h2>
            <button onClick={nextMonth} style={{ padding: "6px 14px" }}>Next &rarr;</button>
          </div>

          <div style={{
            display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: 1,
            background: "var(--border)",
          }}>
            {DAYS.map(d => (
              <div key={d} style={{
                background: "var(--surface)", padding: "8px 4px", textAlign: "center",
                fontWeight: 700, fontSize: 13, color: "var(--muted)",
              }}>{d}</div>
            ))}
            {weeks.flat().map((day, idx) => {
              if (day === null) return <div key={`e${idx}`} style={{ background: "var(--surface)", minHeight: 90 }} />;
              const key = `${year}-${month}-${day}`;
              const dayLeaves = dateToLeaves[key] || [];
              const isToday = year === today.getFullYear() && month === today.getMonth() && day === today.getDate();
              const maxShow = 3;
              return (
                <div key={`d${idx}`} style={{
                  background: "var(--surface)", minHeight: 90, padding: 4,
                  borderTop: isToday ? "3px solid var(--accent)" : "none",
                }}>
                  <div style={{ fontSize: 13, fontWeight: isToday ? 700 : 500, marginBottom: 2, color: isToday ? "var(--accent)" : "var(--text)" }}>
                    {day}
                  </div>
                  {dayLeaves.slice(0, maxShow).map((lv, i) => (
                    <div key={i} style={{
                      fontSize: 11, padding: "1px 4px", borderRadius: 4, marginBottom: 2,
                      color: "#fff",
                      background: STATUS_COLORS[lv.status] || "#0969da",
                      overflow: "hidden", whiteSpace: "nowrap", textOverflow: "ellipsis",
                    }}>
                      {lv.employee.first_name} {lv.employee.last_name?.charAt(0)}. ({lv.leave_type})
                    </div>
                  ))}
                  {dayLeaves.length > maxShow && (
                    <div style={{ fontSize: 11, color: "var(--muted)", paddingLeft: 4 }}>
                      +{dayLeaves.length - maxShow} more
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </>
  );
}
