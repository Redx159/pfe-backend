import { useEffect, useState } from "react";
import {
  fetchMeetings,
  inviteToMeeting,
  cancelMeeting,
} from "../api/meetingsApi";
import { fetchEmployees } from "../api/employeesApi";
import Navbar from "./components/Navbar";
import { getUserFromToken } from "../utils/token";

function formatDateTime(value) {
  if (!value) return "-";

  const date = new Date(value);
  return date.toLocaleString();
}

function Meetings() {
  const currentUser = getUserFromToken();
  const currentUserId = Number(currentUser?.user_id);

  const [meetings, setMeetings] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [inviteOpenId, setInviteOpenId] = useState(null);
  const [selectedByMeeting, setSelectedByMeeting] = useState({});

  const load = async () => {
    try {
      const [m, e] = await Promise.all([
        fetchMeetings(),
        fetchEmployees(),
      ]);

      const meetingsList = Array.isArray(m?.data)
        ? m.data
        : m?.data?.results || m?.data?.data || [];

      const employeesList = Array.isArray(e?.data)
        ? e.data
        : e?.data?.results || e?.data?.data || [];

      setMeetings(meetingsList);
      setEmployees(employeesList);
    } catch (err) {
      console.error("Failed to load meetings or employees", err);
      setMeetings([]);
      setEmployees([]);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const currentEmployee = employees.find((employee) => employee.id === currentUserId);

  const eligibleEmployees = employees.filter((employee) => {
    if (!currentEmployee) return false;

    if (currentEmployee.role === "MANAGER") {
      return employee.role === "EMPLOYEE" && employee.manager === currentUserId;
    }

    if (currentEmployee.role === "ADMIN" || currentEmployee.role === "HR") {
      return employee.role === "EMPLOYEE";
    }

    return false;
  });

  const activeMeetings = meetings.filter((meeting) => !meeting.is_cancelled);
  const cancelledMeetings = meetings.filter((meeting) => meeting.is_cancelled);

  const handleInvite = async (meetingId) => {
    const selected = selectedByMeeting[meetingId] || [];

    if (selected.length === 0) {
      alert("Select at least one employee first.");
      return;
    }

    await inviteToMeeting(meetingId, selected);
    setSelectedByMeeting((prev) => ({ ...prev, [meetingId]: [] }));
    setInviteOpenId(null);
    load();
  };

  const handleCancel = async (id) => {
    if (!window.confirm("Cancel meeting?")) return;

    await cancelMeeting(id);
    load();
  };

  const renderMeetingCard = (meeting) => (
    <div
      key={meeting.id}
      style={{
        border: "1px solid #d0d7de",
        borderRadius: 12,
        padding: 16,
        marginBottom: 16,
        background: meeting.is_cancelled ? "#f6f8fa" : "#ffffff",
        opacity: meeting.is_cancelled ? 0.85 : 1,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
        <div>
          <h3 style={{ margin: "0 0 8px" }}>{meeting.title}</h3>
          <p style={{ margin: "0 0 8px", color: "#57606a" }}>
            {meeting.description || "No description provided."}
          </p>
          <p style={{ margin: "0 0 4px" }}>
            <strong>Starts:</strong> {formatDateTime(meeting.start_time)}
          </p>
          <p style={{ margin: "0 0 4px" }}>
            <strong>Ends:</strong> {formatDateTime(meeting.end_time)}
          </p>
          <p style={{ margin: 0 }}>
            <strong>Created by:</strong>{" "}
            {meeting.created_by?.first_name} {meeting.created_by?.last_name}
          </p>
        </div>

        <div>
          <span
            style={{
              display: "inline-block",
              padding: "6px 10px",
              borderRadius: 999,
              background: meeting.is_cancelled ? "#cf222e" : "#1a7f37",
              color: "#fff",
              fontSize: 12,
              fontWeight: 700,
            }}
          >
            {meeting.is_cancelled ? "Cancelled" : "Active"}
          </span>
        </div>
      </div>

      <div style={{ marginTop: 16 }}>
        <strong>Participants</strong>
        {meeting.participants?.length ? (
          <ul style={{ marginTop: 8, paddingLeft: 20 }}>
            {meeting.participants.map((participant) => (
              <li key={participant.id}>
                {participant.employee?.first_name} {participant.employee?.last_name}{" "}
                ({participant.status})
              </li>
            ))}
          </ul>
        ) : (
          <p style={{ color: "#57606a" }}>No invited participants yet.</p>
        )}
      </div>

      {!meeting.is_cancelled && (
        <div style={{ marginTop: 16 }}>
          <button onClick={() => handleCancel(meeting.id)}>Cancel meeting</button>
          {eligibleEmployees.length > 0 && (
            <button
              style={{ marginLeft: 10 }}
              onClick={() =>
                setInviteOpenId((current) =>
                  current === meeting.id ? null : meeting.id
                )
              }
            >
              {inviteOpenId === meeting.id ? "Hide invite panel" : "Invite employees"}
            </button>
          )}

          {inviteOpenId === meeting.id && eligibleEmployees.length > 0 && (
            <div
              style={{
                marginTop: 12,
                padding: 12,
                border: "1px solid #d8dee4",
                borderRadius: 8,
                background: "#f6f8fa",
              }}
            >
              <p style={{ marginTop: 0 }}>
                Only your direct reports can be invited from the admin panel.
              </p>

              <select
                multiple
                value={selectedByMeeting[meeting.id] || []}
                onChange={(e) =>
                  setSelectedByMeeting((prev) => ({
                    ...prev,
                    [meeting.id]: [...e.target.selectedOptions].map((option) =>
                      Number(option.value)
                    ),
                  }))
                }
                style={{ minWidth: 280, minHeight: 120 }}
              >
                {eligibleEmployees.map((employee) => (
                  <option key={employee.id} value={employee.id}>
                    {employee.first_name} {employee.last_name} - {employee.position}
                  </option>
                ))}
              </select>

              <div style={{ marginTop: 10 }}>
                <button onClick={() => handleInvite(meeting.id)}>Send invites</button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );

  return (
    <>
      <Navbar />

      <div style={{ padding: 20 }}>
        <h2>Meetings</h2>
        <p style={{ color: "#57606a", marginTop: 0 }}>
          Meetings are created from the mobile app. This screen is for reviewing,
          inviting your team, and cancelling existing meetings.
        </p>

        <h3>Active meetings</h3>
        {activeMeetings.length ? (
          activeMeetings.map(renderMeetingCard)
        ) : (
          <p>No active meetings found.</p>
        )}

        <h3 style={{ marginTop: 28 }}>Cancelled meetings</h3>
        {cancelledMeetings.length ? (
          cancelledMeetings.map(renderMeetingCard)
        ) : (
          <p>No cancelled meetings found.</p>
        )}
      </div>
    </>
  );
}

export default Meetings;
