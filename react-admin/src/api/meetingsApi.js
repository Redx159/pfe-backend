import api from "./axios";

export const fetchMeetings = () =>
  api.get("meetings/");

export const createMeeting = (data) =>
  api.post("meetings/", data);

export const inviteToMeeting = (id, employeeIds) =>
  api.post(`meetings/${id}/invite/`, {
    employee_ids: employeeIds,
  });

export const respondToMeeting = (id, status) =>
  api.post(`meetings/${id}/respond/`, {
    status,
  });

export const cancelMeeting = (id) =>
  api.post(`meetings/${id}/cancel/`);
