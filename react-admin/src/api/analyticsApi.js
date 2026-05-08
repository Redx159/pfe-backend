import api from "./axios";

export const fetchDashboardAnalytics = () =>
  api.get("analytics/dashboard/");

export const exportAnalyticsReport = (params = {}) =>
  api.get("analytics/report/", {
    params,
    responseType: "blob",
  });
