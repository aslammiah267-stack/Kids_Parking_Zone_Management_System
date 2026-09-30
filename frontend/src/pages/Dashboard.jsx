import { useEffect, useState } from "react";
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, LineChart, Line, CartesianGrid } from "recharts";
import api, { errorMessage } from "../api";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get("/reports/dashboard/")
      .then((res) => setData(res.data))
      .catch((err) => setError(errorMessage(err)));
  }, []);

  if (error) return <div className="card">{error}</div>;
  if (!data) return <div className="card">Loading dashboard…</div>;

  const cards = [
    ["Total Slots", data.total_slots],
    ["Available", data.available_slots],
    ["Occupied", data.occupied_slots],
    ["Children", data.total_children],
    ["Guardians", data.total_guardians],
    ["Vehicles", data.total_vehicles],
    ["Today Entries", data.today_entries],
    ["Today Exits", data.today_exits],
    ["Today Revenue (BDT)", data.today_revenue],
  ];

  return (
    <div>
      <h1>Dashboard</h1>
      <p style={{ color: "#5b6b7c", marginTop: 0 }}>Kids recreational parking operations overview</p>
      <div className="grid stats">
        {cards.map(([label, value]) => (
          <div className="card" key={label}>
            <div className="stat-label">{label}</div>
            <div className="stat-value">{value}</div>
          </div>
        ))}
      </div>
      <div className="grid two" style={{ marginTop: 16 }}>
        <div className="card">
          <h3>Daily entries / exits</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={data.daily}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="entries" fill="#0f766e" />
              <Bar dataKey="exits" fill="#ea580c" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <h3>Parking occupancy</h3>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={data.occupancy} dataKey="value" nameKey="name" outerRadius={90} label>
                <Cell fill="#14b8a6" />
                <Cell fill="#fb7185" />
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <h3>Revenue (7 days)</h3>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={data.daily}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="revenue" stroke="#1d4ed8" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <h3>Vehicle types</h3>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={data.vehicle_types} dataKey="value" nameKey="name" outerRadius={90} label>
                {data.vehicle_types.map((_, i) => (
                  <Cell key={i} fill={["#0f766e", "#ea580c", "#1d4ed8", "#7c3aed", "#ca8a04"][i % 5]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
