import { BrowserRouter, Routes, Route } from "react-router-dom";
import LoginPage from "./pages/auth/LoginPage";
import Dashboard from "./pages/Dashboard";
import ProtectedRoute from "./auth/ProtectedRoute";
import Leaves from "./pages/leaves/Leaves";
import Employees from "./pages/auth/Employees";
import Attendance from "./pages/Attendance";
import Meetings from "./pages/Meetings";




function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route
  path="/dashboard" 
  element={
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  }
/>
<Route
  path="/leaves"
  element={
    <ProtectedRoute>
      <Leaves />
    </ProtectedRoute>
  }
/>
<Route
  path="/employees"
  element={
    <ProtectedRoute>
      <Employees />
    </ProtectedRoute>
  }
/>
<Route
  path="/attendance"
  element={
    <ProtectedRoute>
      <Attendance />
    </ProtectedRoute>
  }
/>
<Route
  path="/meetings"
  element={
    <ProtectedRoute>
      <Meetings />
    </ProtectedRoute>
  }
/>




      </Routes>
    </BrowserRouter>
  );
}

export default App;
