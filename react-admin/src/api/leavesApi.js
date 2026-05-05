import api from "./axios";

export const fetchLeaves = () =>
  api.get("leaves/leaves/");

export const approveLeave = (id, comment) =>
  api.post(`leaves/leaves/${id}/approve/`, {
    manager_comment: comment,
  });

export const rejectLeave = (id, comment) =>
  api.post(`leaves/leaves/${id}/reject/`, {
    manager_comment: comment,
  });

export const exportLeavesReport = (params = {}) =>
  api.get("leaves/leaves/export/", {
    params,
    responseType: "blob",
  });
