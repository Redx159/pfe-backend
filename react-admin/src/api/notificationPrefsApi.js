import api from "./axios";

export const fetchNotificationPrefs = () =>
  api.get("notifications/preferences/");

export const updateNotificationPrefs = (data) =>
  api.patch("notifications/preferences/", data);
