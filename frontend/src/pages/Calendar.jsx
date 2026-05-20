import { useState, useEffect } from "react";
import api from "../services/api";

export default function Calendar() {
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7));
  const [calendarData, setCalendarData] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCalendar();
  }, [month]);

  const fetchCalendar = async () => {
    setLoading(true);
    try {
      const res = await api.get("/attendance/calendar", { params: { month } });
      setCalendarData(res.data.data || {});
    } catch {
      setCalendarData({});
    } finally {
      setLoading(false);
    }
  };

  const getDaysInMonth = (year, mon) => new Date(year, mon, 0).getDate();
  const getFirstDayOfMonth = (year, mon) => new Date(year, mon - 1, 1).getDay();

  const [year, mon] = month.split("-").map(Number);
  const daysInMonth = getDaysInMonth(year, mon);
  const firstDay = getFirstDayOfMonth(year, mon);

  const prevMonth = () => {
    const d = new Date(year, mon - 2, 1);
    setMonth(d.toISOString().slice(0, 7));
  };

  const nextMonth = () => {
    const d = new Date(year, mon, 1);
    setMonth(d.toISOString().slice(0, 7));
  };

  const weekDays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  const today = new Date().toISOString().split("T")[0];

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Calendar</h1>
          <p className="subtitle">Your attendance overview</p>
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
      ) : (
        <div className="calendar-container">
          <div className="calendar-nav">
            <button className="btn btn-outline" onClick={prevMonth}>&larr; Prev</button>
            <span className="calendar-title">{new Date(year, mon - 1).toLocaleString("default", { month: "long", year: "numeric" })}</span>
            <button className="btn btn-outline" onClick={nextMonth}>Next &rarr;</button>
          </div>

          <div className="calendar-grid">
            {weekDays.map((d) => (
              <div key={d} className="calendar-weekday">{d}</div>
            ))}

            {Array.from({ length: firstDay }).map((_, i) => (
              <div key={`empty-${i}`} className="calendar-day empty"></div>
            ))}

            {Array.from({ length: daysInMonth }).map((_, i) => {
              const day = i + 1;
              const dateStr = `${year}-${String(mon).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
              const data = calendarData[dateStr];
              const isToday = dateStr === today;

              return (
                <div key={day} className={`calendar-day ${data ? "has-data" : ""} ${isToday ? "today" : ""}`}>
                  <span className="day-number">{day}</span>
                  {data && (
                    <div className="day-info">
                      <span className={`status-badge small ${data.status === "present" ? "status-present" : "status-absent"}`}>
                        {data.status}
                      </span>
                      {data.check_in && (
                        <span className="day-time">{new Date(data.check_in).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <div className="calendar-legend">
            <span className="legend-item"><span className="legend-dot present"></span> Present</span>
            <span className="legend-item"><span className="legend-dot absent"></span> Absent</span>
            <span className="legend-item"><span className="legend-dot today-dot"></span> Today</span>
          </div>
        </div>
      )}
    </div>
  );
}
