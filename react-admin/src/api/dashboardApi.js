import api from "./axios";

export const fetchDashboardSummary = () =>
  api.get("auth/dashboard/summary/");
