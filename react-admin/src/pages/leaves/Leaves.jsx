import { useEffect, useState } from "react";
import { fetchLeaves, approveLeave, rejectLeave } from "../../api/leavesApi";
import Navbar from "../components/Navbar";



export default function Leaves() {
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [search, setSearch] = useState("");
  const [leaves, setLeaves] = useState([]);
  const [loading, setLoading] = useState(true);
  const [comments, setComments] = useState({});

  const loadLeaves = async () => {
    const res = await fetchLeaves();
    setLeaves(res.data);
    setLoading(false);
  };

  useEffect(() => {
    loadLeaves();
  }, []);

  const upcomingLeaves = leaves
    .filter((leave) => leave.status === "APPROVED" || leave.status === "PENDING")
    .sort((a, b) => a.start_date.localeCompare(b.start_date))
    .slice(0, 6);

  const pendingCount = leaves.filter((leave) => leave.status === "PENDING").length;
  const approvedCount = leaves.filter((leave) => leave.status === "APPROVED").length;
  const rejectedCount = leaves.filter((leave) => leave.status === "REJECTED").length;

 const handleApprove = async (id) => {
  const comment = comments[id];

  if (!comment || !comment.trim()) {
    alert("Manager comment required");
    return;
  }

  try {
    await approveLeave(id, comment);

    await loadLeaves();

    setComments((prev) => ({ ...prev, [id]: "" }));

  } catch (err) {
    console.error(err);
    alert("Approve failed");
  }
};


  const handleReject = async (id) => {
  const comment = comments[id];

  if (!comment || !comment.trim()) {
    alert("Manager comment required");
    return;
  }

  try {
    await rejectLeave(id, comment);

    // 🔥 REFRESH DATA
    await loadLeaves();

    // clear textarea
    setComments((prev) => ({ ...prev, [id]: "" }));

  } catch (err) {
    console.error(err);
    alert("Reject failed");
  }
};



  if (loading) return <p>Loading...</p>;

  return (
    <><Navbar /><div>
      <h2>Leave Requests</h2>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: 12,
          marginBottom: 20,
        }}
      >
        <div style={{ border: "1px solid #d8dee4", borderRadius: 12, padding: 14 }}>
          <p style={{ margin: 0, color: "#57606a" }}>Pending</p>
          <h3 style={{ marginBottom: 0, color: "#9a6700" }}>{pendingCount}</h3>
        </div>
        <div style={{ border: "1px solid #d8dee4", borderRadius: 12, padding: 14 }}>
          <p style={{ margin: 0, color: "#57606a" }}>Approved</p>
          <h3 style={{ marginBottom: 0, color: "#1a7f37" }}>{approvedCount}</h3>
        </div>
        <div style={{ border: "1px solid #d8dee4", borderRadius: 12, padding: 14 }}>
          <p style={{ margin: 0, color: "#57606a" }}>Rejected</p>
          <h3 style={{ marginBottom: 0, color: "#cf222e" }}>{rejectedCount}</h3>
        </div>
      </div>

      <div
        style={{
          border: "1px solid #d8dee4",
          borderRadius: 12,
          padding: 14,
          marginBottom: 20,
        }}
      >
        <h3 style={{ marginTop: 0 }}>Upcoming Team Leave Calendar</h3>
        {upcomingLeaves.length ? (
          <div style={{ display: "grid", gap: 10 }}>
            {upcomingLeaves.map((leave) => (
              <div key={leave.id} style={{ borderTop: "1px solid #eaeef2", paddingTop: 10 }}>
                <strong>
                  {leave.employee.first_name} {leave.employee.last_name}
                </strong>
                <div>
                  {leave.start_date} → {leave.end_date} ({leave.leave_type})
                </div>
                <div
                  style={{
                    color:
                      leave.status === "APPROVED"
                        ? "#1a7f37"
                        : leave.status === "PENDING"
                          ? "#9a6700"
                          : "#cf222e",
                    fontWeight: "bold",
                  }}
                >
                  {leave.status}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p>No upcoming leave requests.</p>
        )}
      </div>

      <div style={{ marginBottom: 20 }}>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="ALL">All</option>
          <option value="PENDING">Pending</option>
          <option value="APPROVED">Approved</option>
          <option value="REJECTED">Rejected</option>
          <option value="CANCELLED">Cancelled</option>
        </select>

        <input
          placeholder="Search employee..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ marginLeft: 10 }} />
      </div>

      <table border="1" cellPadding="10">
        <thead>
          <tr>
            <th>Employee</th>
            <th>Type</th>
            <th>Dates</th>
            <th>Reason</th>
            <th>Status</th>
            <th>Manager Comment</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>
          {leaves
            .filter((leave) => {
              if (statusFilter !== "ALL" && leave.status !== statusFilter) {
                return false;
              }

              const fullName = `${leave.employee.first_name} ${leave.employee.last_name}`.toLowerCase();

              return fullName.includes(search.toLowerCase());
            })
            .map((leave) => (

              <tr key={leave.id}>
                <td>
                  {leave.employee.first_name}{" "}
                  {leave.employee.last_name}
                </td>
                <td>{leave.leave_type}</td>
                <td>
                  {leave.start_date} → {leave.end_date}
                </td>
                <td>{leave.reason}</td>
                <td>
                  <span
                    style={{
                      fontWeight: "bold",
                      color: leave.status === "APPROVED"
                        ? "green"
                        : leave.status === "REJECTED"
                          ? "red"
                          : leave.status === "PENDING"
                            ? "orange"
                            : "gray",
                    }}
                  >
                    {leave.status}
                  </span>
                </td>

                <td>{leave.manager_comment || "-"}</td>

                <td>
                  {leave.status === "PENDING" && (
                    <>
                      <button onClick={() => handleApprove(leave.id)}>
                        Approve
                      </button>

                      <br />

                      <textarea
                        value={comments[leave.id] || ""}
                        onChange={(e) => setComments({
                          ...comments,
                          [leave.id]: e.target.value,
                        })} />


                      <button onClick={() => handleReject(leave.id)}>
                        Reject
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
        </tbody>
      </table>
    </div></>

  );
}
