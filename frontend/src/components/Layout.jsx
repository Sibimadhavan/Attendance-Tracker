import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="app-layout">
      <nav className="sidebar">
        <div className="sidebar-brand">
          <h2>Attendance<span className="brand-dot"></span></h2>
        </div>
        <ul className="sidebar-nav">
          <li>
            <NavLink to="/dashboard" end className={({ isActive }) => isActive ? "active" : ""}>
              <span className="nav-icon">&#9634;</span>
              Dashboard
            </NavLink>
          </li>
          <li>
            <NavLink to="/attendance" className={({ isActive }) => isActive ? "active" : ""}>
              <span className="nav-icon">&#9776;</span>
              Attendance
            </NavLink>
          </li>
          <li>
            <NavLink to="/calendar" className={({ isActive }) => isActive ? "active" : ""}>
              <span className="nav-icon">&#9781;</span>
              Calendar
            </NavLink>
          </li>
        </ul>
        <div className="sidebar-footer">
          <div className="user-info">
            <span className="user-name">{user?.name}</span>
            <span className="user-email">{user?.email}</span>
          </div>
          <button className="btn btn-ghost" onClick={handleLogout}>Sign out</button>
        </div>
      </nav>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
