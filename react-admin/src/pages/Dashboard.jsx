import { useEffect, useState } from "react";
import { exportDashboardReport, fetchDashboardSummary } from "../api/dashboardApi";
import { useAppShell } from "../context/AppShellContext";
import Navbar from "./components/Navbar";
import { downloadBlob } from "../utils/download";

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

  const handleExport = async () => {
    const today = new Date();
    const month = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}`;
    const res = await exportDashboardReport({ month });
    downloadBlob(res.data, `monthly-dashboard-report-${month}.csv`);
  };

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

  const maxTrend = Math.max(
    1,
    ...summary.attendance_trend.map(
      (item) => item.on_time + item.late + item.absent
    )
  );

  return (
    <>
      <Navbar />

      <div style={{ padding: 20, background: "var(--bg)", minHeight: "100vh" }}>
        <div style={{ marginBottom: 22 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
            <h1 style={{ marginBottom: 6 }}>{t("dashboard.title")}</h1>
            <button onClick={handleExport}>{t("dashboard.exportMonthly")}</button>
          </div>
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
          <StatCard label={t("dashboard.approvedLeaves")} value={summary.totals.approved_leaves} tone="#8250df" />
          <StatCard label={t("dashboard.meetings")} value={summary.totals.meetings} tone="var(--accent)" />
          <StatCard label={t("dashboard.presentToday")} value={summary.totals.today_present} tone="var(--success)" />
          <StatCard label={t("dashboard.lateToday")} value={summary.totals.today_late} tone="var(--warning)" />
          <StatCard label={t("dashboard.absentToday")} value={summary.totals.today_absent} tone="var(--danger)" />
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "2fr 1fr",
            gap: 18,
            alignItems: "start",
            marginBottom: 18,
          }}
        >
          <Panel title={t("dashboard.attendanceTrend")}>
            <div style={{ display: "grid", gap: 12 }}>
              {summary.attendance_trend.map((item) => {
                const total = item.on_time + item.late + item.absent;
                const width = `${(total / maxTrend) * 100}%`;

                return (
                  <div key={item.date}>
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        fontSize: 13,
                        marginBottom: 6,
                      }}
                    >
                      <span>{item.date}</span>
                      <span>
                        {item.on_time} {t("common.onTime").toLowerCase()}, {item.late} {t("common.late").toLowerCase()}, {item.absent} {t("common.absent").toLowerCase()}
                      </span>
                    </div>
                    <div
                      style={{
                        width: "100%",
                        height: 14,
                        borderRadius: 999,
                        background: "var(--border)",
                        overflow: "hidden",
                      }}
                    >
                      <div
                        style={{
                          width,
                          height: "100%",
                          display: "flex",
                        }}
                      >
                        <div
                          style={{
                            width: `${(item.on_time / Math.max(total, 1)) * 100}%`,
                            background: "var(--success)",
                          }}
                        />
                        <div
                          style={{
                            width: `${(item.late / Math.max(total, 1)) * 100}%`,
                            background: "var(--warning)",
                          }}
                        />
                        <div
                          style={{
                            width: `${(item.absent / Math.max(total, 1)) * 100}%`,
                            background: "var(--danger)",
                          }}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </Panel>

          <Panel title={t("dashboard.departmentSplit")}>
            <div style={{ display: "grid", gap: 10 }}>
              {summary.departments.map((item) => (
                <div key={item.department}>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      fontSize: 14,
                      marginBottom: 4,
                    }}
                  >
                    <span>{item.department}</span>
                    <strong>{item.total}</strong>
                  </div>
                  <div
                    style={{
                      width: "100%",
                      height: 10,
                      borderRadius: 999,
                      background: "var(--border)",
                    }}
                  >
                    <div
                      style={{
                        width: `${(item.total / Math.max(summary.totals.employees, 1)) * 100}%`,
                        height: "100%",
                        borderRadius: 999,
                        background: "var(--accent)",
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Panel>
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

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 18,
            alignItems: "start",
          }}
        >
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

          <Panel title={t("dashboard.recentAttendance")}>
            {summary.recent_attendance.length ? (
              <div style={{ display: "grid", gap: 10 }}>
                {summary.recent_attendance.map((item) => (
                  <div key={item.id} style={{ borderTop: "1px solid var(--border)", paddingTop: 10 }}>
                    <strong>{item.employee_name}</strong>
                    <div style={{ fontSize: 14 }}>{item.date}</div>
                    <div style={{ color: statusColor(item.status), fontWeight: 700, fontSize: 13 }}>
                      {item.status}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p>{t("dashboard.noRecentAttendance")}</p>
            )}
          </Panel>
        </div>
      </div>
    </>
  );
}

export default Dashboard;
