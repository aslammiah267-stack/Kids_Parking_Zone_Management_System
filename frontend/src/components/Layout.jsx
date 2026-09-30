import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const links = [
  ["/", "Dashboard"],
  ["/children", "Children"],
  ["/guardians", "Guardians"],
  ["/vehicles", "Vehicles"],
  ["/slots", "Parking Slots"],
  ["/entry-exit", "Entry / Exit"],
  ["/payments", "Payments"],
  ["/history", "Parking History"],
  ["/reports", "Reports"],
  ["/compiler", "KPCL Compiler"],
  ["/settings", "Settings"],
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">KZ</div>
          <div>
            <strong>Kids Parking Zone</strong>
            <div style={{ fontSize: 12, opacity: 0.75 }}>Management System</div>
          </div>
        </div>
        {links.map(([to, label]) => (
          <NavLink key={to} to={to} end={to === "/"} className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
            {label}
          </NavLink>
        ))}
      </aside>
      <div className="main">
        <header className="topbar">
          <div>
            <strong>{user?.role === "ADMIN" ? "Administrator" : "Parking Staff"}</strong>
            <div style={{ color: "#5b6b7c", fontSize: 13 }}>Signed in as {user?.username}</div>
          </div>
          <button
            className="btn secondary"
            onClick={() => {
              logout();
              navigate("/login");
            }}
          >
            Logout
          </button>
        </header>
        <div className="content">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
