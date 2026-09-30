import { createContext, useContext, useEffect, useState } from "react";
import api from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("kpzms_access");
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .get("/auth/me/")
      .then((res) => setUser(res.data))
      .catch(() => {
        localStorage.removeItem("kpzms_access");
        localStorage.removeItem("kpzms_refresh");
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  async function login(username, password) {
    const { data } = await api.post("/auth/login/", { username, password });
    localStorage.setItem("kpzms_access", data.access);
    localStorage.setItem("kpzms_refresh", data.refresh);
    setUser(data.user);
    return data.user;
  }

  function logout() {
    localStorage.removeItem("kpzms_access");
    localStorage.removeItem("kpzms_refresh");
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
