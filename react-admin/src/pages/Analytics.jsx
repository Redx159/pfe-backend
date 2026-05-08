import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, CartesianGrid,
} from "recharts";
import { fetchDashboardAnalytics, exportAnalyticsReport } from "../api/analyticsApi";
import { useAppShell } from "../context/AppShellContext";
import Navbar from "./components/Navbar";
import { downloadBlob } from "../utils/download";

function ErrorBanner({ message, onRetry }) {
  return (
    <div style={{
      border: "1px solid var(--danger)",
      borderRadius: 14, padding: 18, background: "var(--surface)", marginBottom: 20,
    }}>
      <p style={{ color: "var(--danger)", fontWeight: 700, margin: 0 }}>{message}</p>
      {onRetry && (
        <button onClick={onRetry} style={{ marginTop: 12 }}>
          Retry
        </button>
      )}
    </div>
  );
}

const COLORS = ["#1a7f37", "#9a6700", "#cf222e", "#8250df", "#0969da", "#6e7781"];

function StatCard({ label, value, tone = "#0969da" }) {
  return (
    <div style={{
      border: "1px solid var(--border)",
      borderRadius: 14,
      padding: 18,
      background: "var(--surface)",
    }}>
      <p style={{ margin: 0, color: "var(--muted)", fontSize: 13 }}>{label}</p>
      <h2 style={{ margin: "10px 0 0", color: tone }}>{value}</h2>
    </div>
  );
}

function Panel({ title, children }) {
  return (
    <div style={{
      border: "1px solid var(--border)",
      borderRadius: 14,
      padding: 18,
      background: "var(--surface)",
    }}>
      <h3 style={{ marginTop: 0 }}>{title}</h3>
      {children}
    </div>
  );
}

export default function Analytics() {
  const { t } = useAppShell();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = () => {
    setLoading(true);
    setError(null);
    fetchDashboardAnalytics()
      .then((res) => setData(res.data))
      .catch((err) => {
        console.error("Analytics API error:", err);
        setError(err.message || "Failed to load analytics data");
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleExport = async () => {
    const today = new Date();
    const month = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}`;
    const res = await exportAnalyticsReport({ month, format: "pdf" });
    downloadBlob(res.data, `analytics-report-${month}.pdf`);
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <div style={{ padding: 20 }}>{t("common.loading")}</div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Navbar />
        <div style={{ padding: 20, background: "var(--bg)", minHeight: "100vh" }}>
          <ErrorBanner message={`${t("common.unavailable")}: ${error}`} onRetry={loadData} />
        </div>
      </>
    );
  }

  if (!data) {
    return (
      <>
        <Navbar />
        <div style={{ padding: 20 }}>{t("common.loading")}</div>
      </>
    );
  }

  const presencePie = [
    { name: t("common.onTime"), value: data.present_today },
    { name: t("common.late"), value: data.late_today },
    { name: t("common.absent"), value: data.absent_today },
  ].filter((d) => d.value > 0);

  return (
    <>
      <Navbar />
      <div style={{ padding: 20, background: "var(--bg)", minHeight: "100vh" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, marginBottom: 22 }}>
          <div>
            <h1 style={{ marginBottom: 6 }}>{t("analytics.title")}</h1>
            <p style={{ margin: 0, color: "var(--muted)" }}>{t("analytics.subtitle")}</p>
          </div>
          <button onClick={handleExport}>{t("analytics.exportPdf")}</button>
        </div>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
          gap: 14,
          marginBottom: 20,
        }}>
          <StatCard label={t("analytics.totalEmployees")} value={data.total_employees} />
          <StatCard label={t("analytics.attendanceRate")} value={`${data.attendance_rate}%`} tone="var(--success)" />
          <StatCard label={t("analytics.presentToday")} value={data.present_today} tone="var(--success)" />
          <StatCard label={t("analytics.lateToday")} value={data.late_today} tone="var(--warning)" />
          <StatCard label={t("analytics.absentToday")} value={data.absent_today} tone="var(--danger)" />
          <StatCard label={t("analytics.onLeaveToday")} value={data.on_leave_today} tone="#8250df" />
          <StatCard label={t("analytics.pendingLeaves")} value={data.pending_leaves} tone="var(--warning)" />
        </div>

        <div style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 18,
          marginBottom: 18,
        }}>
          <Panel title={t("analytics.monthlyTrend")}>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={data.monthly_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="present" name={t("common.onTime")} fill="#1a7f37" stackId="a" />
                <Bar dataKey="late" name={t("common.late")} fill="#9a6700" stackId="a" />
                <Bar dataKey="absent" name={t("common.absent")} fill="#cf222e" stackId="a" />
              </BarChart>
            </ResponsiveContainer>
          </Panel>

          <Panel title={t("analytics.todayPresence")}>
            {presencePie.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={presencePie}
                    cx="50%"
                    cy="50%"
                    outerRadius={90}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {presencePie.map((_, idx) => (
                      <Cell key={idx} fill={COLORS[idx]} />
                    ))}
                  </Pie>
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p>{t("common.noData")}</p>
            )}
          </Panel>
        </div>

        <div style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 18,
          marginBottom: 18,
        }}>
          <Panel title={t("analytics.leaveByType")}>
            {data.leave_by_type.length > 0 ? (
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie
                    data={data.leave_by_type}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="count"
                    nameKey="type"
                    label={({ type, count }) => `${type}: ${count}`}
                  >
                    {data.leave_by_type.map((_, idx) => (
                      <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                    ))}
                  </Pie>
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p>{t("common.noData")}</p>
            )}
          </Panel>

          <Panel title={t("analytics.departmentStats")}>
            {data.department_stats.length > 0 ? (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={data.department_stats} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis type="number" tick={{ fontSize: 12 }} />
                  <YAxis dataKey="name" type="category" tick={{ fontSize: 12 }} width={100} />
                  <Tooltip />
                  <Bar dataKey="present" name={t("common.onTime")} fill="#1a7f37" stackId="a" />
                  <Bar dataKey="late" name={t("common.late")} fill="#9a6700" stackId="a" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p>{t("common.noData")}</p>
            )}
          </Panel>
        </div>
      </div>
    </>
  );
}
