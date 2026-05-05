import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav style={{ padding: 15, borderBottom: "1px solid #ccc" }}>
      <Link to="/dashboard">Dashboard</Link> |{" "}
      <Link to="/employees">Employees</Link> |{" "}
      <Link to="/leaves">Leaves</Link> |{" "}
      <Link to="/attendance">Attendance</Link> |{" "}
      <Link to="/meetings">Meetings</Link> 
    </nav>
  );
}
