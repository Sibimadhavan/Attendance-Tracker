import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

export default function Dashboard() {
  const { user } = useAuth();
  const [today, setToday] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchToday();
  }, []);

  const fetchToday = async () => {
    try {
      const res = await api.get("/attendance/today");
      setToday(res.data);
    } catch {
      setToday({ date: new Date().toISOString().split("T")[0], status: "absent", check_in: null, check_out: null });
    } finally {
      setLoading(false);
    }
  };

  const handleCheckIn = async () => {
    try {
      const res = await api.post("/attendance/check-in");
      setToday((prev) => ({ ...prev, ...res.data, status: "present" }));
    } catch (err) {
      alert(err.response?.data?.detail || "Check-in failed");
    }
  };

  const handleCheckOut = async () => {
    try {
      await api.post("/attendance/check-out");
      fetchToday();
    } catch (err) {
      alert(err.response?.data?.detail || "Check-out failed");
    }
  };

  if (loading) return <div className="loading">Loading...</div>;

  const isCheckedIn = today?.check_in && !today?.check_out;
  const isCheckedOut = today?.check_out;

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p className="subtitle">Welcome back, {user?.name}</p>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <div className="card-label">Status</div>
          <div className={`status-badge ${today?.status === "present" ? "status-present" : "status-absent"}`}>
            {today?.status === "present" ? "Present" : "Not checked in"}
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-label">Check In</div>
          <div className="card-value">
            {today?.check_in ? new Date(today.check_in).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "--:--"}
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-label">Check Out</div>
          <div className="card-value">
            {today?.check_out ? new Date(today.check_out).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "--:--"}
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-label">Date</div>
          <div className="card-value">{today?.date}</div>
        </div>
      </div>

      <div className="action-bar">
        {!today?.check_in && (
          <button className="btn btn-success" onClick={handleCheckIn}>Check In</button>
        )}
        {isCheckedIn && (
          <button className="btn btn-danger" onClick={handleCheckOut}>Check Out</button>
        )}
        {isCheckedOut && (
          <span className="done-label">All done for today</span>
        )}
      </div>

      <div className="nav-links">
        <Link to="/attendance" className="btn btn-outline">View Attendance</Link>
        <Link to="/calendar" className="btn btn-outline">Calendar</Link>
      </div>
    </div>
  );
}
