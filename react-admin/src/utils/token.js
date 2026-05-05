import { jwtDecode } from "jwt-decode";

export const getUserFromToken = () => {
  const token = localStorage.getItem("access");

  if (!token) return null;

  return jwtDecode(token);
};
