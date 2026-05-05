import api from "../api/axios";

export const fetchDepartments = () =>
  api.get("auth/departments/");
