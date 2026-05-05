import { useEffect, useState } from "react";
import {
  fetchMeetings,
  createMeeting,
  inviteToMeeting,
  cancelMeeting,
} from "../api/meetingsApi";

import { fetchEmployees } from "../api/employeesApi";
import Navbar from "./components/Navbar";

function Meetings() {

  const [meetings, setMeetings] = useState([]);
  const [employees, setEmployees] = useState([]);

  const [form, setForm] = useState({
    title: "",
    description: "",
    start_time: "",
    end_time: "",
  });

  const [selected, setSelected] = useState([]);

  const load = async () => {
    try {
      const [m, e] = await Promise.all([
        fetchMeetings(),
        fetchEmployees(),
      ]);

      const md = m?.data;
      const meetingsList = Array.isArray(md) ? md : md?.results || md?.data || [];

      const ed = e?.data;
      const employeesList = Array.isArray(ed) ? ed : ed?.results || ed?.data || [];

      setMeetings(meetingsList);
      setEmployees(employeesList);
    } catch (err) {
      console.error('Failed to load meetings or employees', err);
      setMeetings([]);
      setEmployees([]);
    }
  };

  useEffect(() => {
    load();
  }, []);

  // --------------------

  const handleCreate = async () => {

    await createMeeting(form);

    setForm({
      title: "",
      description: "",
      start_time: "",
      end_time: "",
    });

    load();
  };

  const handleInvite = async (meetingId) => {

    await inviteToMeeting(meetingId, selected);

    setSelected([]);
    load();
  };

  const handleCancel = async (id) => {

    if (!confirm("Cancel meeting?")) return;

    await cancelMeeting(id);

    load();
  };

  // --------------------

  return (
    <>
      <Navbar />

      <h2>Meetings</h2>

      {/* CREATE */}

      <h3>Create meeting</h3>

      <input
        placeholder="Title"
        value={form.title}
        onChange={(e) =>
          setForm({ ...form, title: e.target.value })
        }
      />

      <textarea
        placeholder="Description"
        value={form.description}
        onChange={(e) =>
          setForm({ ...form, description: e.target.value })
        }
      />

      <input
        type="datetime-local"
        value={form.start_time}
        onChange={(e) =>
          setForm({ ...form, start_time: e.target.value })
        }
      />

      <input
        type="datetime-local"
        value={form.end_time}
        onChange={(e) =>
          setForm({ ...form, end_time: e.target.value })
        }
      />

      <button onClick={handleCreate}>
        Create
      </button>

      <hr />

      {/* LIST */}

      {meetings.map((m) => (

        <div key={m.id} style={{ border: "1px solid gray", margin: 10, padding: 10 }}>

          <h4>{m.title}</h4>
          <p>{m.description}</p>
          <p>
            {m.start_time} → {m.end_time}
          </p>

          {!m.is_cancelled && (
            <button onClick={() => handleCancel(m.id)}>
              Cancel
            </button>
          )}

          <h5>Invite employees</h5>

          <select
            multiple
            value={selected}
            onChange={(e) =>
              setSelected(
                [...e.target.selectedOptions].map(o => o.value)
              )
            }
          >
            {employees.map((e) => (
              <option key={e.id} value={e.id}>
                {e.first_name} {e.last_name}
              </option>
            ))}
          </select>

          <br />

          <button onClick={() => handleInvite(m.id)}>
            Invite
          </button>

        </div>
      ))}
    </>
  );
}

export default Meetings;
