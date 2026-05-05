import { useEffect, useState } from "react";
import { fetchEmployees, updateEmployee } from "../../api/employeesApi";
import { fetchDepartments } from "../../api/departmentsApi";
import Navbar from "../components/Navbar";
import { approveEmployee } from "../../api/employeesApi";
import { deleteEmployee } from "../../api/employeesApi";



export default function Employees() {
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [editing, setEditing] = useState(null);

  const loadData = async () => {
    const [emps, deps] = await Promise.all([
      fetchEmployees(),
      fetchDepartments(),
    ]);

    setEmployees(emps.data);
    setDepartments(deps.data);
  };

  useEffect(() => {
    loadData();
  }, []);

  const managers = employees.filter((emp) =>
    ["MANAGER", "HR", "ADMIN"].includes(emp.role)
  );

  const totalEmployees = employees.length;
  const activeEmployees = employees.filter((emp) => emp.is_active).length;
  const pendingApprovals = employees.filter((emp) => !emp.is_active).length;

  const handleSave = async () => {
    await updateEmployee(editing.id, {
      role: editing.role,
      department_id: editing.department?.id,
      manager_id: editing.manager || null,
    });

    setEditing(null);
    loadData();
  };

  return (
    <><Navbar />
      <div style={{ padding: 20 }}>
        <h2>Employees</h2>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: 12,
            marginBottom: 18,
          }}
        >
          <div style={{ border: "1px solid #d8dee4", borderRadius: 12, padding: 14 }}>
            <p style={{ margin: 0, color: "#57606a" }}>Total employees</p>
            <h3 style={{ marginBottom: 0 }}>{totalEmployees}</h3>
          </div>
          <div style={{ border: "1px solid #d8dee4", borderRadius: 12, padding: 14 }}>
            <p style={{ margin: 0, color: "#57606a" }}>Active accounts</p>
            <h3 style={{ marginBottom: 0, color: "#1a7f37" }}>{activeEmployees}</h3>
          </div>
          <div style={{ border: "1px solid #d8dee4", borderRadius: 12, padding: 14 }}>
            <p style={{ margin: 0, color: "#57606a" }}>Pending approvals</p>
            <h3 style={{ marginBottom: 0, color: "#9a6700" }}>{pendingApprovals}</h3>
          </div>
        </div>

        <table border="1" cellPadding="8">
        <thead>
          <tr>
            <th>Name</th>
            <th>Position</th>
            <th>Role</th>
            <th>Department</th>
            <th>Manager</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>

        <tbody>
          {employees.map((emp) => (
            <tr key={emp.id}>
              <td>{emp.first_name} {emp.last_name}</td>
              <td>{emp.position || "-"}</td>
              <td>{emp.role}</td>
              <td>{emp.department?.name || "-"}</td>
              <td>
                {emp.manager_name || "-"}
              </td>
              <td style={{ color: emp.is_active ? "#1a7f37" : "#9a6700", fontWeight: 700 }}>
                {emp.is_active ? "Active" : "Pending"}
              </td>
              <td>
                {!emp.is_active && (
                  <button
                    style={{ background: "green", color: "white" }}
                    onClick={async () => {
                      await approveEmployee(emp.id);
                      loadData();
                    }}
                  >
                    Approve
                  </button>
                )}
                <button
                  style={{ color: "red" }}
                  onClick={async () => {
                    if (!window.confirm("Delete this user?")) return;

                    await deleteEmployee(emp.id);
                    loadData();
                  }}
                >
                  Delete
                </button>


                <button onClick={() => setEditing(emp)}>
                  Edit
                </button>
              </td>

            </tr>
          ))}
        </tbody>
      </table>

      {editing && (
        <div style={{ border: "1px solid gray", padding: 20, marginTop: 20 }}>
          <h3>Edit Employee</h3>

          <label>Role</label>
          <br />
          <select
            value={editing.role}
            onChange={(e) =>
              setEditing({ ...editing, role: e.target.value })
            }
          >
            <option value="EMPLOYEE">EMPLOYEE</option>
            <option value="MANAGER">MANAGER</option>
            <option value="HR">HR</option>
            <option value="ADMIN">ADMIN</option>
          </select>

          <br /><br />

          <label>Department</label>
          <br />
          <select
            value={editing.department?.id || ""}
            onChange={(e) =>
              setEditing({
                ...editing,
                department: {
                  id: e.target.value,
                },
              })
            }
          >
            <option value="">---</option>
            {departments.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>

          <br /><br />

          <label>Manager</label>
          <br />
          <select
            value={editing.manager || ""}
            onChange={(e) =>
              setEditing({
                ...editing,
                manager: e.target.value ? Number(e.target.value) : null,
              })
            }
          >
            <option value="">---</option>
            {managers
              .filter((manager) => manager.id !== editing.id)
              .map((manager) => (
                <option key={manager.id} value={manager.id}>
                  {manager.first_name} {manager.last_name} - {manager.role}
                </option>
              ))}
          </select>

          <br /><br />

          <button onClick={handleSave}>Save</button>
          <button onClick={() => setEditing(null)}>Cancel</button>
        </div>
      )}
      </div>
    </>);
}
