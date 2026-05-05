import api from "./axios";

export const fetchMeetings = () =>
  api.get("meetings/meetings/");

export const createMeeting = (data) =>
  api.post("meetings/meetings/", data);

export const inviteToMeeting = (id, employeeIds) =>
  api.post(`meetings/meetings/${id}/invite/`, {
    employee_ids: employeeIds,
  });

export const respondToMeeting = (id, status) =>
  api.post(`meetings/meetings/${id}/respond/`, {
    status,
  });

export const cancelMeeting = (id) =>
  api.post(`meetings/meetings/${id}/cancel/`);
