import api from "./axios";

export const fetchDashboardSummary = () =>
  api.get("auth/dashboard/summary/");

export const exportDashboardReport = (params = {}) =>
  api.get("auth/dashboard/export/", {
    params,
    responseType: "blob",
  });
