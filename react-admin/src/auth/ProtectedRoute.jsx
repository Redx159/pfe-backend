import { Navigate } from "react-router-dom";
import { getUserFromToken } from "../utils/token";

export default function ProtectedRoute({ children }) {
  const user = getUserFromToken();

  if (!user) {
    return <Navigate to="/" />;
  }

  return children;
}
