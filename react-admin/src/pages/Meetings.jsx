import { useEffect, useState } from "react";
import { fetchMeetings } from "../api/meetingsApi";
import { useAppShell } from "../context/AppShellContext";
import Navbar from "./components/Navbar";

function formatDateTime(value) {
  if (!value) return "-";
  return new Date(value).toLocaleString();
}

const FILTERS = ["all", "upcoming", "active", "ended", "cancelled"];

function Meetings() {
  const { t } = useAppShell();
  const [meetings, setMeetings] = useState([]);
  const [filter, setFilter] = useState("all");

  const load = async (currentFilter) => {
    try {
      const m = await fetchMeetings(
        currentFilter === "all" ? null : currentFilter
      );
      const list = Array.isArray(m?.data)
        ? m.data
        : m?.data?.results || m?.data?.data || [];
      setMeetings(list);
    } catch (err) {
      console.error("Failed to load meetings", err);
      setMeetings([]);
    }
  };

  useEffect(() => {
    load(filter);
  }, [filter]);

  const renderMeetingCard = (meeting) => {
    const now = new Date();
    const start = new Date(meeting.start_time);
    const end = new Date(meeting.end_time);
    const isActive = !meeting.is_cancelled && start <= now && end >= now;
    const isUpcoming = !meeting.is_cancelled && start > now;
    const isEnded = !meeting.is_cancelled && end < now;

    let badge = null;
    if (meeting.is_cancelled) {
      badge = { label: t("common.cancelled"), color: "#cf222e" };
    } else if (isActive) {
      badge = { label: t("common.active"), color: "#1a7f37" };
    } else if (isUpcoming) {
      badge = { label: t("meetings.upcoming"), color: "#9a6700" };
    } else {
      badge = { label: t("meetings.ended"), color: "#656d76" };
    }

    return (
      <div
        key={meeting.id}
        style={{
          border: "1px solid var(--border)",
          borderRadius: 12,
          padding: 16,
          marginBottom: 16,
          opacity: meeting.is_cancelled ? 0.85 : 1,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
          <div style={{ flex: 1 }}>
            <h3 style={{ margin: "0 0 8px" }}>{meeting.title}</h3>
            {meeting.description && (
              <p style={{ margin: "0 0 8px", color: "var(--muted)" }}>
                {meeting.description}
              </p>
            )}
            <p style={{ margin: "0 0 4px" }}>
              <strong>{t("meetings.starts")}:</strong> {formatDateTime(meeting.start_time)}
            </p>
            <p style={{ margin: "0 0 4px" }}>
              <strong>{t("meetings.ends")}:</strong> {formatDateTime(meeting.end_time)}
            </p>
            <p style={{ margin: "0 0 4px" }}>
              <strong>{t("meetings.mode")}:</strong>{" "}
              {meeting.is_online
                ? t("meetings.online")
                : t("meetings.inPerson")}
              {meeting.is_online && meeting.meeting_url && (
                <> &mdash; <a href={meeting.meeting_url} target="_blank" rel="noopener noreferrer">{meeting.meeting_url}</a></>
              )}
              {!meeting.is_online && meeting.location && (
                <> &mdash; {meeting.location}</>
              )}
            </p>
            <p style={{ margin: 0 }}>
              <strong>{t("meetings.createdBy")}:</strong>{" "}
              {meeting.created_by?.first_name} {meeting.created_by?.last_name}
            </p>
          </div>

          <div style={{ flexShrink: 0 }}>
            <span
              style={{
                display: "inline-block",
                padding: "6px 10px",
                borderRadius: 999,
                background: badge.color,
                color: "#fff",
                fontSize: 12,
                fontWeight: 700,
              }}
            >
              {badge.label}
            </span>
          </div>
        </div>

        <div style={{ marginTop: 16 }}>
          <strong>{t("meetings.participants")}</strong>
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
            <p style={{ color: "var(--muted)" }}>{t("meetings.noParticipants")}</p>
          )}
        </div>
      </div>
    );
  };

  return (
    <>
      <Navbar />
      <div style={{ padding: 20 }}>
        <h2>{t("meetings.title")}</h2>

        <div style={{ display: "flex", gap: 8, marginBottom: 20, flexWrap: "wrap" }}>
          {FILTERS.map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              style={{
                padding: "6px 14px",
                borderRadius: 999,
                border: "1px solid var(--border)",
                background: filter === f ? "var(--accent)" : "var(--surface)",
                color: filter === f ? "#fff" : "inherit",
                cursor: "pointer",
                fontWeight: filter === f ? 700 : 400,
              }}
            >
              {t(`meetings.filter${f.charAt(0).toUpperCase() + f.slice(1)}`)}
            </button>
          ))}
        </div>

        {meetings.length ? (
          meetings.map(renderMeetingCard)
        ) : (
          <p>{t("common.noData")}</p>
        )}
      </div>
    </>
  );
}

export default Meetings;
