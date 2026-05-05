import api from "./axios";

export const loginRequest = async (credentials) => {
  const res = await api.post("/token/", credentials);

  localStorage.setItem("access", res.data.access);
  localStorage.setItem("refresh", res.data.refresh);

  return res.data;
};
