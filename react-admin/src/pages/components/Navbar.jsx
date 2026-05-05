import { Link } from "react-router-dom";
import { useAppShell } from "../../context/AppShellContext";

export default function Navbar() {
  const { t, language, setLanguage, themePreference, setThemePreference } = useAppShell();

  return (
    <nav
      style={{
        padding: 15,
        borderBottom: "1px solid var(--border)",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        gap: 16,
        background: "var(--surface)",
      }}
    >
      <div style={{ display: "flex", gap: 14, flexWrap: "wrap" }}>
        <Link to="/dashboard">{t("nav.dashboard")}</Link>
        <Link to="/employees">{t("nav.employees")}</Link>
        <Link to="/leaves">{t("nav.leaves")}</Link>
        <Link to="/attendance">{t("nav.attendance")}</Link>
        <Link to="/meetings">{t("nav.meetings")}</Link>
      </div>

      <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
        <label style={{ fontSize: 13, color: "var(--muted)" }}>
          {t("nav.language")}
        </label>
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          style={{ width: 90, padding: "6px 8px" }}
        >
          <option value="en">EN</option>
          <option value="fr">FR</option>
        </select>

        <label style={{ fontSize: 13, color: "var(--muted)" }}>
          {t("nav.theme")}
        </label>
        <select
          value={themePreference}
          onChange={(e) => setThemePreference(e.target.value)}
          style={{ width: 90, padding: "6px 8px" }}
        >
          <option value="light">{t("nav.light")}</option>
          <option value="dark">{t("nav.dark")}</option>
          <option value="auto">{t("nav.auto")}</option>
        </select>
      </div>
    </nav>
  );
}
