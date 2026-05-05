import { useEffect, useState } from "react";
import { fetchAllAttendance } from "../api/attendanceApi";
import { useAppShell } from "../context/AppShellContext";
import Navbar from "./components/Navbar";

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

export default function AttendanceTable() {
  const { t } = useAppShell();
  const [rows, setRows] = useState([]);

  useEffect(() => {
    fetchAllAttendance().then(res => setRows(res.data));
  }, []);

  return (
    <> <Navbar />
    <div style={{ padding: 20 }}>
    <h2>{t("attendance.title")}</h2>
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
        {rows.map(r => (
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
            <td>{r.work_duration_str || "-"}</td>
          </tr>
        ))}
      </tbody>
    </table></div></>
  );
}
