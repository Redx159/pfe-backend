import { useEffect, useState } from "react";
import { exportAttendanceReport, fetchAllAttendance } from "../api/attendanceApi";
import { useAppShell } from "../context/AppShellContext";
import Navbar from "./components/Navbar";
import { downloadBlob } from "../utils/download";

function getStatusStyle(status) {
  if (status === "ON_TIME") {
    return { color: "#1a7f37", fontWeight: 700 };
  }

  if (status === "LATE") {
    return { color: "#9a6700", fontWeight: 700 };
  }

  if (status === "ABSENT") {
    return { color: "#cf222e", fontWeight: 700 };
  }

  return { color: "#24292f", fontWeight: 700 };
}

function getDurationStyle(durationStr) {
  if (!durationStr || durationStr === "-") return {};
  const parts = durationStr.split(":");
  const hours = parseInt(parts[0], 10);
  if (isNaN(hours)) return {};
  return {
    color: hours >= 8 ? "#1a7f37" : "#cf222e",
    fontWeight: 700,
  };
}

export default function AttendanceTable() {
  const { t } = useAppShell();
  const [rows, setRows] = useState([]);
  const [search, setSearch] = useState("");

  const handleExport = async () => {
    const today = new Date();
    const month = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}`;
    const res = await exportAttendanceReport({ month });
    downloadBlob(res.data, `attendance-report-${month}.csv`);
  };

  useEffect(() => {
    fetchAllAttendance().then(res => setRows(res.data));
  }, []);

  const filtered = search.trim()
    ? rows.filter((r) => r.employee_name?.toLowerCase().includes(search.toLowerCase()))
    : rows;

  return (
    <> <Navbar />
    <div style={{ padding: 20 }}>
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
    <h2>{t("attendance.title")}</h2>
    <button onClick={handleExport}>{t("attendance.export")}</button>
    </div>
    <div style={{ marginBottom: 12 }}>
      <input
        placeholder={t("common.searchEmployee")}
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        style={{ maxWidth: 300 }}
      />
    </div>
    <table>
      <thead>
        <tr>
          <th>{t("attendance.employee")}</th>
          <th>{t("attendance.date")}</th>
          <th>{t("attendance.checkIn")}</th>
          <th>{t("attendance.status")}</th>
          <th>{t("attendance.checkOut")}</th>
          <th>{t("attendance.duration")}</th>
        </tr>
      </thead>
      <tbody>
        {filtered.map(r => (
          <tr key={r.id}>
            <td>{r.employee_name}</td>
            <td>{r.date}</td>
            <td>{r.check_in_time || "-"}</td>
            <td style={getStatusStyle(r.status)}>
              {r.status === "ON_TIME"
                ? t("common.onTime")
                : r.status === "LATE"
                  ? t("common.late")
                  : r.status === "ABSENT"
                    ? t("common.absent")
                    : r.status}
            </td>
            <td>{r.check_out_time || "-"}</td>
            <td style={getDurationStyle(r.work_duration_str)}>{r.work_duration_str || "-"}</td>
          </tr>
        ))}
      </tbody>
    </table></div></>
  );
}
