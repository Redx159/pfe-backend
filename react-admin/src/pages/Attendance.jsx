import { useEffect, useState } from "react";
import { myAttendance } from "../api/attendanceApi";
import Navbar from "./components/Navbar";

export default function AttendanceTable() {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    myAttendance().then(res => setRows(res.data));
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
            <td>{r.status}</td>
            <td>{r.check_out_time || "-"}</td>
            <td>{r.work_duration_str || "-"}</td>
          </tr>
        ))}
      </tbody>
    </table></>
  );
}
