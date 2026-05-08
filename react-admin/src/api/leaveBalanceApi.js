import api from "./axios";

export const fetchLeaveHistory = (year) =>
  api.get("leaves/leaves/history/", { params: { year } });

export const fetchLeaveProjections = () =>
  api.get("leaves/leaves/projections/");
