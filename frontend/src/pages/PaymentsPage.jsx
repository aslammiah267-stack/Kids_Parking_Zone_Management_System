import { useEffect, useState } from "react";
import api, { errorMessage, unwrapList } from "../api";
import { useToast } from "../context/ToastContext";

export default function PaymentsPage() {
  const toast = useToast();
  const [rows, setRows] = useState([]);
  const [vehicleId, setVehicleId] = useState("");

  async function load() {
    const { data } = await api.get("/payments/", { params: { page_size: 100 } });
    setRows(unwrapList(data));
  }

  useEffect(() => {
    load().catch((e) => toast.show(errorMessage(e), "error"));
  }, []);

  async function collect() {
    try {
      await api.post("/payments/", { vehicle_id: vehicleId.toUpperCase() });
      toast.show("Payment marked completed");
      setVehicleId("");
      load();
    } catch (err) {
      toast.show(errorMessage(err), "error");
    }
  }

  return (
    <div>
      <div className="toolbar">
        <div>
          <h1>Payments</h1>
          <p style={{ color: "#5b6b7c" }}>Collect parking fees after exit.</p>
        </div>
        <div className="row">
          <input placeholder="Vehicle ID" value={vehicleId} onChange={(e) => setVehicleId(e.target.value)} />
          <button className="btn" onClick={collect}>Mark paid</button>
        </div>
      </div>
      <div className="card table-wrap">
        <table>
          <thead>
            <tr>
              <th>Payment ID</th>
              <th>Vehicle</th>
              <th>Record</th>
              <th>Duration</th>
              <th>Fee</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((p) => (
              <tr key={p.payment_id}>
                <td>PAY{p.payment_id}</td>
                <td>{p.vehicle_id}</td>
                <td>{p.record_id}</td>
                <td>{p.duration_minutes} min</td>
                <td>{p.fee}</td>
                <td>{p.amount}</td>
                <td><span className={`badge ${p.payment_status === "COMPLETED" ? "ok" : "warn"}`}>{p.payment_status}</span></td>
                <td>{new Date(p.payment_time).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {!rows.length && <div className="empty">No payments yet.</div>}
      </div>
    </div>
  );
}
