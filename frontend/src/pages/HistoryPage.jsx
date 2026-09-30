import { useEffect, useState } from "react";
import api, { errorMessage, unwrapList } from "../api";
import { useToast } from "../context/ToastContext";

export default function HistoryPage() {
  const toast = useToast();
  const [rows, setRows] = useState([]);
  const [filters, setFilters] = useState({ vehicle: "", slot: "", from: "", to: "", search: "" });

  async function load() {
    const { data } = await api.get("/parking-records/", { params: { ...filters, page_size: 200 } });
    setRows(unwrapList(data));
  }

  useEffect(() => {
    load().catch((e) => toast.show(errorMessage(e), "error"));
  }, []);

  function exportCsv() {
    const header = ["Record ID", "Vehicle", "Child", "Slot", "Entry", "Exit", "Duration", "Fee", "Payment"];
    const body = rows.map((r) => [r.record_id, r.vehicle_id, r.child_id, r.slot_id, r.entry_time, r.exit_time, r.duration_minutes, r.fee, r.payment_status].join(","));
    const blob = new Blob([[header.join(","), ...body].join("\n")], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "parking-history.csv";
    a.click();
  }

  return (
    <div>
      <div className="toolbar">
        <div>
          <h1>Parking History</h1>
          <p style={{ color: "#5b6b7c" }}>Search, filter and export parking records.</p>
        </div>
        <div className="row">
          <button className="btn secondary" onClick={() => window.print()}>Print</button>
          <button className="btn" onClick={exportCsv}>Export CSV</button>
        </div>
      </div>
      <div className="card">
        <div className="row" style={{ marginBottom: 12 }}>
          <input placeholder="Search" value={filters.search} onChange={(e) => setFilters({ ...filters, search: e.target.value })} />
          <input placeholder="Vehicle" value={filters.vehicle} onChange={(e) => setFilters({ ...filters, vehicle: e.target.value })} />
          <input placeholder="Slot" value={filters.slot} onChange={(e) => setFilters({ ...filters, slot: e.target.value })} />
          <input type="date" value={filters.from} onChange={(e) => setFilters({ ...filters, from: e.target.value })} />
          <input type="date" value={filters.to} onChange={(e) => setFilters({ ...filters, to: e.target.value })} />
          <button className="btn secondary" onClick={load}>Filter</button>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Record ID</th>
                <th>Vehicle</th>
                <th>Child</th>
                <th>Slot</th>
                <th>Entry Time</th>
                <th>Exit Time</th>
                <th>Duration</th>
                <th>Fee</th>
                <th>Payment Status</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.record_id}>
                  <td>{r.record_id}</td>
                  <td>{r.vehicle_id}</td>
                  <td>{r.child_id}</td>
                  <td>{r.slot_id}</td>
                  <td>{r.entry_time ? new Date(r.entry_time).toLocaleString() : "—"}</td>
                  <td>{r.exit_time ? new Date(r.exit_time).toLocaleString() : "—"}</td>
                  <td>{r.duration_minutes ?? r.live_duration_minutes ?? "—"}</td>
                  <td>{r.fee ?? r.live_fee ?? "—"}</td>
                  <td>{r.payment_status || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!rows.length && <div className="empty">No history records.</div>}
        </div>
      </div>
    </div>
  );
}
