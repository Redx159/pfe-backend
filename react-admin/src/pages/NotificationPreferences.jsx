import { useEffect, useState } from "react";
import { fetchNotificationPrefs, updateNotificationPrefs } from "../api/notificationPrefsApi";
import { useAppShell } from "../context/AppShellContext";
import Navbar from "./components/Navbar";

export default function NotificationPreferences() {
  const { t } = useAppShell();
  const [prefs, setPrefs] = useState(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    fetchNotificationPrefs().then((res) => setPrefs(res.data));
  }, []);

  const toggle = (field) => {
    setPrefs({ ...prefs, [field]: !prefs[field] });
    setSaved(false);
  };

  const save = async () => {
    await updateNotificationPrefs(prefs);
    setSaved(true);
  };

  if (!prefs) return <><Navbar /><div style={{ padding: 20 }}>{t("common.loading")}</div></>;

  return (
    <>
      <Navbar />
      <div style={{ padding: 20, background: "var(--bg)", minHeight: "100vh" }}>
        <h1 style={{ marginBottom: 6 }}>{t("notificationPrefs.title")}</h1>
        <p style={{ margin: "0 0 20px", color: "var(--muted)" }}>{t("notificationPrefs.subtitle")}</p>

        <div style={{ border: "1px solid var(--border)", borderRadius: 14, padding: 18, background: "var(--surface)", maxWidth: 500 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 0", borderBottom: "1px solid var(--border)" }}>
            <div>
              <strong>{t("notificationPrefs.meetingInvites")}</strong>
              <p style={{ margin: "2px 0 0", fontSize: 13, color: "var(--muted)" }}>{t("notificationPrefs.meetingInvitesDesc")}</p>
            </div>
            <input type="checkbox" checked={prefs.meeting_invites} onChange={() => toggle("meeting_invites")} />
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 0", borderBottom: "1px solid var(--border)" }}>
            <div>
              <strong>{t("notificationPrefs.leaveStatus")}</strong>
              <p style={{ margin: "2px 0 0", fontSize: 13, color: "var(--muted)" }}>{t("notificationPrefs.leaveStatusDesc")}</p>
            </div>
            <input type="checkbox" checked={prefs.leave_status} onChange={() => toggle("leave_status")} />
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 0", borderBottom: "1px solid var(--border)" }}>
            <div>
              <strong>{t("notificationPrefs.reminders")}</strong>
              <p style={{ margin: "2px 0 0", fontSize: 13, color: "var(--muted)" }}>{t("notificationPrefs.remindersDesc")}</p>
            </div>
            <input type="checkbox" checked={prefs.reminders} onChange={() => toggle("reminders")} />
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 0" }}>
            <div>
              <strong style={{ color: prefs.vacation_mode ? "#cf222e" : "inherit" }}>{t("notificationPrefs.vacationMode")}</strong>
              <p style={{ margin: "2px 0 0", fontSize: 13, color: "var(--muted)" }}>{t("notificationPrefs.vacationModeDesc")}</p>
            </div>
            <input type="checkbox" checked={prefs.vacation_mode} onChange={() => toggle("vacation_mode")} />
          </div>

          <div style={{ marginTop: 16, display: "flex", gap: 8, alignItems: "center" }}>
            <button onClick={save}>{t("common.save")}</button>
            {saved && <span style={{ color: "#1a7f37", fontSize: 13 }}>{t("common.saved")}</span>}
          </div>
        </div>
      </div>
    </>
  );
}
