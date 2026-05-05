import { useEffect, useState } from "react";
import { fetchAllAttendance } from "../api/attendanceApi";
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
  const [rows, setRows] = useState([]);

  useEffect(() => {
    fetchAllAttendance().then(res => setRows(res.data));
  }, []);

  return (
    <> <Navbar />
    <table border="1">
      <thead>
        <tr>
          <th>Employee</th>
          <th>Date</th>
          <th>Check-in</th>
          <th>Status</th>
          <th>Check-out</th>
          <th>Duration</th>
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
                ? "On Time"
                : r.status === "LATE"
                  ? "Late"
                  : r.status === "ABSENT"
                    ? "Absent"
                    : r.status}
            </td>
            <td>{r.check_out_time || "-"}</td>
            <td>{r.work_duration_str || "-"}</td>
          </tr>
        ))}
      </tbody>
    </table></>
  );
}
