import { useState, useEffect } from "react";
import { useSearchParams, Link, useNavigate } from "react-router-dom";
import api from "../services/api";

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [message, setMessage] = useState("Verifying your email...");
  const [done, setDone] = useState(false);

  const token = searchParams.get("token");

  useEffect(() => {
    if (!token) {
      setMessage("No verification token provided. Please check your email link.");
      return;
    }

    api.post("/auth/verify", { token })
      .then((res) => {
        setMessage(res.data.message);
        setDone(true);
        setTimeout(() => navigate("/login"), 2500);
      })
      .catch((err) => {
        setMessage(err.response?.data?.detail || "Verification failed. The link may have expired.");
      });
  }, [token, navigate]);

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Verifying</h1>
        <p className="auth-subtitle">One moment please.</p>
        <div className={`alert ${done ? "alert-success" : "alert-info"}`}>{message}</div>
        {done && (
          <p className="auth-link">
            Redirecting to sign in... <Link to="/login">Go now</Link>
          </p>
        )}
        {!token && (
          <p className="auth-link">
            <Link to="/login">Back to sign in</Link>
          </p>
        )}
      </div>
    </div>
  );
}
