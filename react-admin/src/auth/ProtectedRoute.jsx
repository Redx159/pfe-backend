import { Navigate } from "react-router-dom";
import { getUserFromToken } from "../utils/token";

const ALLOWED_ROLES = ["ADMIN", "HR"];

export default function ProtectedRoute({ children }) {
  const user = getUserFromToken();

  if (!user) {
    return <Navigate to="/" />;
  }

  if (!ALLOWED_ROLES.includes(user.role)) {
    localStorage.clear();
    return <Navigate to="/" />;
  }

  return children;
}
