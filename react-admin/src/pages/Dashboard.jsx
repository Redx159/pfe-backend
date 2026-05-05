import { useEffect, useState } from "react";
import { fetchDashboardSummary } from "../api/dashboardApi";
import Navbar from "./components/Navbar";

function StatCard({ label, value, tone = "#0969da" }) {
  return (
    <div
      style={{
        border: "1px solid #d8dee4",
        borderRadius: 14,
        padding: 18,
        background: "#fff",
      }}
    >
      <p style={{ margin: 0, color: "#57606a", fontSize: 13 }}>{label}</p>
      <h2 style={{ margin: "10px 0 0", color: tone }}>{value}</h2>
    </div>
  );
}

function Panel({ title, children }) {
  return (
    <div
      style={{
        border: "1px solid #d8dee4",
        borderRadius: 14,
        padding: 18,
        background: "#fff",
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
        <div style={{ padding: 20 }}>Loading dashboard...</div>
      </>
    );
  }

  if (!summary) {
    return (
      <>
        <Navbar />
        <div style={{ padding: 20 }}>Dashboard data is unavailable.</div>
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

      <div style={{ padding: 20, background: "#f6f8fa", minHeight: "100vh" }}>
        <div style={{ marginBottom: 22 }}>
          <h1 style={{ marginBottom: 6 }}>Dashboard</h1>
          <p style={{ margin: 0, color: "#57606a" }}>
            Viewing {summary.scope === "company" ? "company-wide" : "team"} activity.
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
          <StatCard label="Employees" value={summary.totals.employees} />
          <StatCard label="Active Accounts" value={summary.totals.active_accounts} tone="#1a7f37" />
          <StatCard label="Pending Leaves" value={summary.totals.pending_leaves} tone="#9a6700" />
          <StatCard label="Approved Leaves" value={summary.totals.approved_leaves} tone="#8250df" />
          <StatCard label="Meetings" value={summary.totals.meetings} tone="#0969da" />
          <StatCard label="Present Today" value={summary.totals.today_present} tone="#1a7f37" />
          <StatCard label="Late Today" value={summary.totals.today_late} tone="#9a6700" />
          <StatCard label="Absent Today" value={summary.totals.today_absent} tone="#cf222e" />
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
          <Panel title="Attendance Trend">
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
                        {item.on_time} on time, {item.late} late, {item.absent} absent
                      </span>
                    </div>
                    <div
                      style={{
                        width: "100%",
                        height: 14,
                        borderRadius: 999,
                        background: "#eaeef2",
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
                            background: "#1a7f37",
                          }}
                        />
                        <div
                          style={{
                            width: `${(item.late / Math.max(total, 1)) * 100}%`,
                            background: "#d4a72c",
                          }}
                        />
                        <div
                          style={{
                            width: `${(item.absent / Math.max(total, 1)) * 100}%`,
                            background: "#cf222e",
                          }}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </Panel>

          <Panel title="Department Split">
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
                      background: "#eaeef2",
                    }}
                  >
                    <div
                      style={{
                        width: `${(item.total / Math.max(summary.totals.employees, 1)) * 100}%`,
                        height: "100%",
                        borderRadius: 999,
                        background: "#0969da",
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
          <Panel title="Pending Leave Requests">
            {summary.pending_leaves.length ? (
              <div style={{ display: "grid", gap: 10 }}>
                {summary.pending_leaves.map((leave) => (
                  <div key={leave.id} style={{ borderTop: "1px solid #eaeef2", paddingTop: 10 }}>
                    <strong>{leave.employee_name}</strong>
                    <div style={{ fontSize: 14, color: "#57606a" }}>
                      {leave.leave_type} • {leave.start_date} to {leave.end_date}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p>No pending leave requests.</p>
            )}
          </Panel>

          <Panel title="Upcoming Meetings">
            {summary.upcoming_meetings.length ? (
              <div style={{ display: "grid", gap: 10 }}>
                {summary.upcoming_meetings.map((meeting) => (
                  <div key={meeting.id} style={{ borderTop: "1px solid #eaeef2", paddingTop: 10 }}>
                    <strong>{meeting.title}</strong>
                    <div style={{ fontSize: 14, color: "#57606a" }}>
                      {new Date(meeting.start_time).toLocaleString()}
                    </div>
                    <div style={{ fontSize: 13, color: "#57606a" }}>
                      Created by {meeting.created_by}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p>No upcoming meetings.</p>
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
          <Panel title="Upcoming Leave Calendar">
            {summary.upcoming_leaves.length ? (
              <div style={{ display: "grid", gap: 10 }}>
                {summary.upcoming_leaves.map((leave) => (
                  <div key={leave.id} style={{ borderTop: "1px solid #eaeef2", paddingTop: 10 }}>
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
              <p>No upcoming leave items.</p>
            )}
          </Panel>

          <Panel title="Recent Attendance">
            {summary.recent_attendance.length ? (
              <div style={{ display: "grid", gap: 10 }}>
                {summary.recent_attendance.map((item) => (
                  <div key={item.id} style={{ borderTop: "1px solid #eaeef2", paddingTop: 10 }}>
                    <strong>{item.employee_name}</strong>
                    <div style={{ fontSize: 14 }}>{item.date}</div>
                    <div style={{ color: statusColor(item.status), fontWeight: 700, fontSize: 13 }}>
                      {item.status}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p>No recent attendance records.</p>
            )}
          </Panel>
        </div>
      </div>
    </>
  );
}

export default Dashboard;
