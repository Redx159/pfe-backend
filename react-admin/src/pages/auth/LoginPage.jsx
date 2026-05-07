import { useEffect, useState } from "react";
import { loginRequest } from "../../api/authApi";
import { useAppShell } from "../../context/AppShellContext";

export default function LoginPage() {
  const { t, language, setLanguage, themePreference, setThemePreference } = useAppShell();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await loginRequest({ username, password });
      window.location.href = "/dashboard";
    } catch (err) {
      const msg = err?.response?.data?.detail || t("login.invalid");
      setError(msg);
    }
  };

  return (
    <div style={{ maxWidth: 440, margin: "100px auto", background: "var(--surface)", padding: 24, borderRadius: 16, border: "1px solid var(--border)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 10, marginBottom: 18 }}>
        <select value={language} onChange={(e) => setLanguage(e.target.value)} style={{ width: 90 }}>
          <option value="en">EN</option>
          <option value="fr">FR</option>
        </select>
        <select value={themePreference} onChange={(e) => setThemePreference(e.target.value)} style={{ width: 110 }}>
          <option value="light">{t("nav.light")}</option>
          <option value="dark">{t("nav.dark")}</option>
          <option value="auto">{t("nav.auto")}</option>
        </select>
      </div>

      <h2>{t("login.title")}</h2>
      <p style={{ color: "var(--muted)" }}>{t("login.subtitle")}</p>

      {error && <p style={{ color: "var(--danger)" }}>{error}</p>}

      <form onSubmit={handleSubmit}>
        <input
          placeholder={t("login.username")}
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <br />
        <br />

        <input
          type="password"
          placeholder={t("login.password")}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <br />
        <br />

        <button type="submit">{t("login.submit")}</button>
      </form>
    </div>
  );
}
