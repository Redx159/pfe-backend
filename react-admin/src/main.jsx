import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { AppShellProvider } from "./context/AppShellContext";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AppShellProvider>
      <App />
    </AppShellProvider>
  </React.StrictMode>
);
