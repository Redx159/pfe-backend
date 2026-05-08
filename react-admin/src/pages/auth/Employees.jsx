import { useEffect, useState } from "react";
import { fetchEmployees, createEmployee, updateEmployee, deleteEmployee, approveEmployee, fetchDepartments } from "../../api/employeesApi";
import { useAppShell } from "../../context/AppShellContext";
import Navbar from "../components/Navbar";

const INITIAL = { first_name: "", last_name: "", email: "", username: "", password: "", position: "", department_id: "", manager_id: "", role: "EMPLOYEE", hire_date: "", phone_number: "" };

export default function Employees() {
  const { t } = useAppShell();
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [editing, setEditing] = useState(null);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState(INITIAL);

  const loadData = async () => {
    const [emps, deps] = await Promise.all([fetchEmployees(), fetchDepartments()]);
    setEmployees(emps.data);
    setDepartments(deps.data);
  };

  useEffect(() => { loadData(); }, []);

  const managers = employees.filter((emp) => ["MANAGER", "HR", "ADMIN"].includes(emp.role));
  const total = employees.length;
  const active = employees.filter((e) => e.is_active).length;
  const pending = employees.filter((e) => !e.is_active).length;

  const handleCreate = async () => {
    await createEmployee(form);
    setCreating(false);
    setForm(INITIAL);
    loadData();
  };

  const handleSave = async () => {
    await updateEmployee(editing.id, {
      role: editing.role,
      department_id: editing.department?.id || null,
      manager_id: editing.manager || null,
      position: editing.position,
      phone_number: editing.phone_number || "",
    });
    setEditing(null);
    loadData();
  };

  return (
    <>
      <Navbar />
      <div style={{ padding: 20 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h2>{t("employees.title")}</h2>
          <button onClick={() => setCreating(true)}>+ {t("employees.create")}</button>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12, marginBottom: 18 }}>
          <div style={{ border: "1px solid #d8dee4", borderRadius: 12, padding: 14 }}>
            <p style={{ margin: 0, color: "var(--muted)" }}>{t("employees.totalEmployees")}</p>
            <h3 style={{ marginBottom: 0 }}>{total}</h3>
          </div>
          <div style={{ border: "1px solid #d8dee4", borderRadius: 12, padding: 14 }}>
            <p style={{ margin: 0, color: "var(--muted)" }}>{t("dashboard.activeAccounts")}</p>
            <h3 style={{ marginBottom: 0, color: "#1a7f37" }}>{active}</h3>
          </div>
          <div style={{ border: "1px solid #d8dee4", borderRadius: 12, padding: 14 }}>
            <p style={{ margin: 0, color: "var(--muted)" }}>{t("employees.pendingApprovals")}</p>
            <h3 style={{ marginBottom: 0, color: "#9a6700" }}>{pending}</h3>
          </div>
        </div>

        <table border="1" cellPadding="8">
          <thead>
            <tr>
              <th>{t("employees.name")}</th>
              <th>{t("employees.position")}</th>
              <th>{t("employees.role")}</th>
              <th>{t("employees.department")}</th>
              <th>{t("employees.manager")}</th>
              <th>{t("employees.status")}</th>
              <th>{t("employees.actions")}</th>
            </tr>
          </thead>
          <tbody>
            {employees.map((emp) => (
              <tr key={emp.id}>
                <td>{emp.first_name} {emp.last_name}</td>
                <td>{emp.position || "-"}</td>
                <td>{emp.role}</td>
                <td>{emp.department?.name || "-"}</td>
                <td>{emp.manager_name || "-"}</td>
                <td style={{ color: emp.is_active ? "#1a7f37" : "#9a6700", fontWeight: 700 }}>
                  {emp.is_active ? t("common.active") : t("common.pending")}
                </td>
                <td>
                  {!emp.is_active && (
                    <button style={{ background: "green", color: "white" }} onClick={async () => { await approveEmployee(emp.id); loadData(); }}>{t("common.approve")}</button>
                  )}
                  <button style={{ color: "red" }} onClick={async () => { if (!window.confirm("Delete this user?")) return; await deleteEmployee(emp.id); loadData(); }}>{t("common.delete")}</button>
                  <button onClick={() => setEditing(emp)}>{t("common.edit")}</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {creating && (
          <div style={{ border: "1px solid var(--border)", borderRadius: 14, padding: 20, marginTop: 20, background: "var(--surface)" }}>
            <h3>{t("employees.createEmployee")}</h3>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <div><label>{t("employees.firstName")}</label><input value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} /></div>
              <div><label>{t("employees.lastName")}</label><input value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} /></div>
              <div><label>{t("employees.email")}</label><input value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></div>
              <div><label>{t("employees.username")}</label><input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} /></div>
              <div><label>{t("employees.password")}</label><input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></div>
              <div><label>{t("employees.position")}</label><input value={form.position} onChange={(e) => setForm({ ...form, position: e.target.value })} /></div>
              <div><label>{t("employees.department")}</label>
                <select value={form.department_id} onChange={(e) => setForm({ ...form, department_id: e.target.value ? Number(e.target.value) : null })}>
                  <option value="">---</option>
                  {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
                </select>
              </div>
              <div><label>{t("employees.role")}</label>
                <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
                  <option value="EMPLOYEE">EMPLOYEE</option>
                  <option value="MANAGER">MANAGER</option>
                  <option value="HR">HR</option>
                  <option value="ADMIN">ADMIN</option>
                </select>
              </div>
              <div><label>{t("employees.manager")}</label>
                <select value={form.manager_id} onChange={(e) => setForm({ ...form, manager_id: e.target.value ? Number(e.target.value) : null })}>
                  <option value="">---</option>
                  {managers.filter((m) => !form.username || m.username !== form.username).map((m) => (
                    <option key={m.id} value={m.id}>{m.first_name} {m.last_name}</option>
                  ))}
                </select>
              </div>
              <div><label>{t("employees.hireDate")}</label><input type="date" value={form.hire_date} onChange={(e) => setForm({ ...form, hire_date: e.target.value })} /></div>
              <div><label>{t("employees.phone")}</label><input value={form.phone_number} onChange={(e) => setForm({ ...form, phone_number: e.target.value })} /></div>
            </div>
            <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
              <button onClick={handleCreate}>{t("common.save")}</button>
              <button onClick={() => { setCreating(false); setForm(INITIAL); }}>{t("common.cancel")}</button>
            </div>
          </div>
        )}

        {editing && (
          <div style={{ border: "1px solid var(--border)", borderRadius: 14, padding: 20, marginTop: 20, background: "var(--surface)" }}>
            <h3>{t("employees.editEmployee")}</h3>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <div><label>{t("employees.role")}</label>
                <select value={editing.role} onChange={(e) => setEditing({ ...editing, role: e.target.value })}>
                  <option value="EMPLOYEE">EMPLOYEE</option>
                  <option value="MANAGER">MANAGER</option>
                  <option value="HR">HR</option>
                  <option value="ADMIN">ADMIN</option>
                </select>
              </div>
              <div><label>{t("employees.department")}</label>
                <select value={editing.department?.id || ""} onChange={(e) => setEditing({ ...editing, department: e.target.value ? { id: Number(e.target.value) } : null })}>
                  <option value="">---</option>
                  {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
                </select>
              </div>
              <div><label>{t("employees.manager")}</label>
                <select value={editing.manager || ""} onChange={(e) => setEditing({ ...editing, manager: e.target.value ? Number(e.target.value) : null })}>
                  <option value="">---</option>
                  {managers.filter((m) => m.id !== editing.id).map((m) => (
                    <option key={m.id} value={m.id}>{m.first_name} {m.last_name} - {m.role}</option>
                  ))}
                </select>
              </div>
              <div><label>{t("employees.position")}</label><input value={editing.position || ""} onChange={(e) => setEditing({ ...editing, position: e.target.value })} /></div>
              <div><label>{t("employees.phone")}</label><input value={editing.phone_number || ""} onChange={(e) => setEditing({ ...editing, phone_number: e.target.value })} /></div>
            </div>
            <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
              <button onClick={handleSave}>{t("common.save")}</button>
              <button onClick={() => setEditing(null)}>{t("common.cancel")}</button>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
