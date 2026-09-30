import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import api, { errorMessage } from "../api";

export default function ReportsPage() {
  const [dash, setDash] = useState(null);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.get("/reports/dashboard/"), api.get("/reports/summary/")])
      .then(([a, b]) => {
        setDash(a.data);
        setSummary(b.data);
      })
      .catch((e) => setError(errorMessage(e)));
  }, []);

  if (error) return <div className="card">{error}</div>;
  if (!dash || !summary) return <div className="card">Loading reports…</div>;

  return (
    <div>
      <h1>Reports</h1>
      <div className="grid stats">
        <div className="card"><div className="stat-label">Total records</div><div className="stat-value">{summary.total_records}</div></div>
        <div className="card"><div className="stat-label">Active</div><div className="stat-value">{summary.active}</div></div>
        <div className="card"><div className="stat-label">Exited unpaid</div><div className="stat-value">{summary.exited}</div></div>
        <div className="card"><div className="stat-label">Paid</div><div className="stat-value">{summary.paid}</div></div>
        <div className="card"><div className="stat-label">Total revenue</div><div className="stat-value">{summary.total_revenue}</div></div>
      </div>
      <div className="card" style={{ marginTop: 16 }}>
        <h3>Daily activity</h3>
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={dash.daily}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="entries" fill="#0f766e" />
            <Bar dataKey="exits" fill="#ea580c" />
            <Bar dataKey="revenue" fill="#1d4ed8" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
