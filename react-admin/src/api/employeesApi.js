import api from "./axios";

export const fetchEmployees = () =>
  api.get("auth/employees/");

export const updateEmployee = (id, data) =>
  api.patch(`auth/employees/${id}/`, data);

export const approveEmployee = (id) =>
  api.post(`auth/approve/${id}/`);
export const deleteEmployee = (id) =>
  api.delete(`auth/employees/${id}/`);
