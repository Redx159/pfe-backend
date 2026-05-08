import { useEffect, useState } from "react";
import { fetchDashboardSummary } from "../api/dashboardApi";
import { useAppShell } from "../context/AppShellContext";
import Navbar from "./components/Navbar";

function StatCard({ label, value, tone = "#0969da" }) {
  return (
    <div
      style={{
        border: "1px solid var(--border)",
        borderRadius: 14,
        padding: 18,
        background: "var(--surface)",
      }}
    >
      <p style={{ margin: 0, color: "var(--muted)", fontSize: 13 }}>{label}</p>
      <h2 style={{ margin: "10px 0 0", color: tone }}>{value}</h2>
    </div>
  );
}

function Panel({ title, children }) {
  return (
    <div
      style={{
        border: "1px solid var(--border)",
        borderRadius: 14,
        padding: 18,
        background: "var(--surface)",
      }}
    >
      <h3 style={{ marginTop: 0 }}>{title}</h3>
      {children}
    </div>
  );
}

function statusColor(status) {
  if (status === "APPROVED" || status === "ON_TIME") return "#1a7f37";
  if (status === "PENDING" || status === "LATE") return "#9a6700";
  if (status === "REJECTED" || status === "ABSENT") return "#cf222e";
  if (status === "CANCELLED") return "#6e7781";
  return "#24292f";
}

function Dashboard() {
  const { t } = useAppShell();
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardSummary()
      .then((res) => setSummary(res.data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <>
        <Navbar />
        <div style={{ padding: 20 }}>{t("common.loading")}</div>
      </>
    );
  }

  if (!summary) {
    return (
      <>
        <Navbar />
        <div style={{ padding: 20 }}>{t("common.unavailable")}</div>
      </>
    );
  }

  return (
    <>
      <Navbar />

      <div style={{ padding: 20, background: "var(--bg)", minHeight: "100vh" }}>
        <div style={{ marginBottom: 22 }}>
          <h1 style={{ marginBottom: 6 }}>{t("dashboard.title")}</h1>
          <p style={{ margin: 0, color: "var(--muted)" }}>
            {summary.scope === "company" ? t("dashboard.companyScope") : t("dashboard.teamScope")}
          </p>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: 14,
            marginBottom: 20,
          }}
        >
          <StatCard label={t("dashboard.employees")} value={summary.totals.employees} />
          <StatCard label={t("dashboard.activeAccounts")} value={summary.totals.active_accounts} tone="var(--success)" />
          <StatCard label={t("dashboard.pendingLeaves")} value={summary.totals.pending_leaves} tone="var(--warning)" />
          <StatCard label={t("dashboard.presentToday")} value={summary.totals.today_present} tone="var(--success)" />
          <StatCard label={t("dashboard.lateToday")} value={summary.totals.today_late} tone="var(--warning)" />
          <StatCard label={t("dashboard.absentToday")} value={summary.totals.today_absent} tone="var(--danger)" />
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 18,
            alignItems: "start",
            marginBottom: 18,
          }}
        >
          <Panel title={t("dashboard.pendingLeaveRequests")}>
            {summary.pending_leaves.length ? (
              <div style={{ display: "grid", gap: 10 }}>
                {summary.pending_leaves.map((leave) => (
                  <div key={leave.id} style={{ borderTop: "1px solid var(--border)", paddingTop: 10 }}>
                    <strong>{leave.employee_name}</strong>
                    <div style={{ fontSize: 14, color: "var(--muted)" }}>
                      {leave.leave_type} • {leave.start_date} to {leave.end_date}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p>{t("dashboard.noPendingLeaves")}</p>
            )}
          </Panel>

          <Panel title={t("dashboard.upcomingMeetings")}>
            {summary.upcoming_meetings.length ? (
              <div style={{ display: "grid", gap: 10 }}>
                {summary.upcoming_meetings.map((meeting) => (
                  <div key={meeting.id} style={{ borderTop: "1px solid var(--border)", paddingTop: 10 }}>
                    <strong>{meeting.title}</strong>
                    <div style={{ fontSize: 14, color: "var(--muted)" }}>
                      {new Date(meeting.start_time).toLocaleString()}
                    </div>
                    <div style={{ fontSize: 13, color: "var(--muted)" }}>
                      {t("dashboard.createdBy")} {meeting.created_by}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p>{t("dashboard.noUpcomingMeetings")}</p>
            )}
          </Panel>
        </div>

        <Panel title={t("dashboard.upcomingLeaveCalendar")}>
          {summary.upcoming_leaves.length ? (
            <div style={{ display: "grid", gap: 10 }}>
              {summary.upcoming_leaves.map((leave) => (
                <div key={leave.id} style={{ borderTop: "1px solid var(--border)", paddingTop: 10 }}>
                  <strong>{leave.employee_name}</strong>
                  <div style={{ fontSize: 14 }}>
                    {leave.start_date} to {leave.end_date}
                  </div>
                  <div style={{ color: statusColor(leave.status), fontWeight: 700, fontSize: 13 }}>
                    {leave.status}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p>{t("dashboard.noUpcomingLeaves")}</p>
          )}
        </Panel>
      </div>
    </>
  );
}

export default Dashboard;
