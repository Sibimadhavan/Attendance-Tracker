import { useState, useEffect } from "react";
import api from "../services/api";

export default function AttendanceList() {
  const [records, setRecords] = useState([]);
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAttendance();
  }, [month]);

  const fetchAttendance = async () => {
    setLoading(true);
    try {
      const res = await api.get("/attendance/all", { params: { month } });
      setRecords(res.data.records);
    } catch {
      setRecords([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Attendance</h1>
          <p className="subtitle">All users' attendance records</p>
        </div>
        <div className="filter-group">
          <input
            type="month"
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            className="input-month"
          />
        </div>
      </div>

      {loading ? (
        <div className="loading">Loading...</div>
      ) : records.length === 0 ? (
        <div className="empty-state">No attendance records found for this period.</div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Date</th>
                <th>Check In</th>
                <th>Check Out</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {records.map((r, i) => (
                <tr key={i}>
                  <td className="td-name">{r.name}</td>
                  <td className="td-email">{r.email}</td>
                  <td className="td-date">{r.date}</td>
                  <td>{r.check_in ? new Date(r.check_in).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "-"}</td>
                  <td>{r.check_out ? new Date(r.check_out).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "-"}</td>
                  <td>
                    <span className={`status-badge small ${r.status === "present" ? "status-present" : "status-absent"}`}>
                      {r.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
