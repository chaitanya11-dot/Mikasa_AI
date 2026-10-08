import React, { useState, useEffect } from "react";
import Home from "./pages/Home";
import Login from "./pages/Login";

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return localStorage.getItem("mikasa_auth") === "true";
  });

  const handleLogin = () => {
    localStorage.setItem("mikasa_auth", "true");
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem("mikasa_auth");
    setIsAuthenticated(false);
  };

  return isAuthenticated ? <Home onLogout={handleLogout} /> : <Login onLogin={handleLogin} />;
}
