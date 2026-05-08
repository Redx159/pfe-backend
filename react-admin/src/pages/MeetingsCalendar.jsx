import { useEffect, useMemo, useState } from "react";
import { fetchMeetings } from "../api/meetingsApi";
import { useAppShell } from "../context/AppShellContext";
import Navbar from "./components/Navbar";

const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const TYPE_COLORS = {
  ONLINE: "#8250df",
  IN_PERSON: "#0969da",
};

export default function MeetingsCalendar() {
  const { t } = useAppShell();
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [year, setYear] = useState(new Date().getFullYear());
  const [month, setMonth] = useState(new Date().getMonth());

  useEffect(() => {
    fetchMeetings()
      .then((res) => setMeetings(res.data))
      .finally(() => setLoading(false));
  }, []);

  const active = useMemo(() => meetings.filter((m) => !m.is_cancelled), [meetings]);

  const dateToMeetings = useMemo(() => {
    const map = {};
    for (const m of active) {
      const start = new Date(m.start_time);
      const key = `${start.getFullYear()}-${start.getMonth()}-${start.getDate()}`;
      if (!map[key]) map[key] = [];
      map[key].push(m);
    }
    return map;
  }, [active]);

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
        <div style={{ marginBottom: 22 }}>
          <h1 style={{ marginBottom: 6 }}>{t("meetingsCalendar.title")}</h1>
          <p style={{ margin: 0, color: "var(--muted)" }}>{t("meetingsCalendar.subtitle")}</p>
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
              const dayMeetings = dateToMeetings[key] || [];
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
                  {dayMeetings.slice(0, maxShow).map((m, i) => (
                    <div key={i} style={{
                      fontSize: 11, padding: "1px 4px", borderRadius: 4, marginBottom: 2,
                      color: "#fff",
                      background: m.is_online ? TYPE_COLORS.ONLINE : TYPE_COLORS.IN_PERSON,
                      overflow: "hidden", whiteSpace: "nowrap", textOverflow: "ellipsis",
                    }}>
                      {m.title}
                    </div>
                  ))}
                  {dayMeetings.length > maxShow && (
                    <div style={{ fontSize: 11, color: "var(--muted)", paddingLeft: 4 }}>
                      +{dayMeetings.length - maxShow} more
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
