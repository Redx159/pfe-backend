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
