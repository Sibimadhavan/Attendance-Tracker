import { useState, useEffect } from "react";
import { useSearchParams, Link, useNavigate } from "react-router-dom";
import api from "../services/api";

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [message, setMessage] = useState("Verifying...");
  const [done, setDone] = useState(false);

  const token = searchParams.get("token");

  useEffect(() => {
    if (!token) {
      setMessage("No verification token provided.");
      return;
    }

    api.post("/auth/verify", { token })
      .then((res) => {
        setMessage(res.data.message);
        setDone(true);
        setTimeout(() => navigate("/login"), 2000);
      })
      .catch((err) => {
        setMessage(err.response?.data?.detail || "Verification failed");
      });
  }, [token, navigate]);

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Email Verification</h1>
        <div className="alert alert-info">{message}</div>
        {done && (
          <p className="auth-link">
            Redirecting to login... <Link to="/login">Go now</Link>
          </p>
        )}
        {!token && (
          <p className="auth-link">
            <Link to="/login">Back to login</Link>
          </p>
        )}
      </div>
    </div>
  );
}
