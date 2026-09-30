import { useEffect, useState } from "react";
import api, { errorMessage, unwrapList } from "../api";
import { useToast } from "../context/ToastContext";
import Modal from "../components/Modal";

export default function VehiclesPage() {
  const toast = useToast();
  const [rows, setRows] = useState([]);
  const [children, setChildren] = useState([]);
  const [q, setQ] = useState("");
  const [form, setForm] = useState(null);
  const [history, setHistory] = useState(null);

  async function load() {
    const [vehicles, kids] = await Promise.all([
      api.get("/vehicles/", { params: { search: q, page_size: 100 } }),
      api.get("/children/", { params: { page_size: 100 } }),
    ]);
    setRows(unwrapList(vehicles.data));
    setChildren(unwrapList(kids.data));
  }

  useEffect(() => {
    load().catch((e) => toast.show(errorMessage(e), "error"));
  }, []);

  async function save(e) {
    e.preventDefault();
    try {
      const payload = { vehicle_id: form.vehicle_id, vehicle_type: form.vehicle_type, child: form.child };
      if (form.mode === "edit") await api.put(`/vehicles/${form.vehicle_id}/`, payload);
      else await api.post("/vehicles/", payload);
      toast.show("Vehicle saved");
      setForm(null);
      load();
    } catch (err) {
      toast.show(errorMessage(err), "error");
    }
  }

  async function remove(id) {
    if (!confirm(`Delete vehicle ${id}?`)) return;
    try {
      await api.delete(`/vehicles/${id}/`);
      toast.show("Deleted");
      load();
    } catch (err) {
      toast.show(errorMessage(err), "error");
    }
  }

  async function showHistory(id) {
    try {
      const { data } = await api.get(`/vehicles/${id}/history/`);
      setHistory({ id, rows: data });
    } catch (err) {
      toast.show(errorMessage(err), "error");
    }
  }

  return (
    <div>
      <div className="toolbar">
        <div>
          <h1>Vehicles</h1>
          <p style={{ color: "#5b6b7c" }}>Toy cars, bikes and other recreational vehicles.</p>
        </div>
        <button className="btn" onClick={() => setForm({ mode: "create", vehicle_id: "", vehicle_type: "CAR", child: children[0]?.child_id || "" })}>
          Register vehicle
        </button>
      </div>
      <div className="card">
        <div className="toolbar">
          <input placeholder="Search vehicles" value={q} onChange={(e) => setQ(e.target.value)} />
          <button className="btn secondary" onClick={load}>Search</button>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Vehicle ID</th>
                <th>Type</th>
                <th>Child</th>
                <th>Status</th>
                <th>Current Slot</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((v) => (
                <tr key={v.vehicle_id}>
                  <td>{v.vehicle_id}</td>
                  <td>{v.vehicle_type}</td>
                  <td>{v.child_name} ({v.child})</td>
                  <td><span className={`badge ${v.status === "OUT" ? "ok" : "warn"}`}>{v.status}</span></td>
                  <td>{v.current_slot || "—"}</td>
                  <td className="row">
                    <button className="btn ghost" onClick={() => setForm({ ...v, mode: "edit" })}>Edit</button>
                    <button className="btn ghost" onClick={() => showHistory(v.vehicle_id)}>History</button>
                    <button className="btn ghost" onClick={() => remove(v.vehicle_id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!rows.length && <div className="empty">No vehicles found.</div>}
        </div>
      </div>
      {form && (
        <Modal title={form.mode === "edit" ? "Edit vehicle" : "Register vehicle"} onClose={() => setForm(null)}>
          <form onSubmit={save}>
            <div className="field">
              <label>Vehicle ID</label>
              <input value={form.vehicle_id} disabled={form.mode === "edit"} onChange={(e) => setForm({ ...form, vehicle_id: e.target.value.toUpperCase() })} required />
            </div>
            <div className="field">
              <label>Type</label>
              <select value={form.vehicle_type} onChange={(e) => setForm({ ...form, vehicle_type: e.target.value })}>
                <option>CAR</option>
                <option>BIKE</option>
                <option>TOY</option>
                <option>BUS</option>
                <option>OTHER</option>
              </select>
            </div>
            <div className="field">
              <label>Child</label>
              <select value={form.child} onChange={(e) => setForm({ ...form, child: e.target.value })} required>
                {children.map((c) => (
                  <option key={c.child_id} value={c.child_id}>{c.child_id} — {c.name}</option>
                ))}
              </select>
            </div>
            <button className="btn">Save</button>
          </form>
        </Modal>
      )}
      {history && (
        <Modal title={`History for ${history.id}`} onClose={() => setHistory(null)}>
          <table>
            <thead>
              <tr><th>Record</th><th>Slot</th><th>Status</th><th>Fee</th></tr>
            </thead>
            <tbody>
              {history.rows.map((r) => (
                <tr key={r.record_id}>
                  <td>{r.record_id}</td>
                  <td>{r.slot_id}</td>
                  <td>{r.status}</td>
                  <td>{r.fee ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Modal>
      )}
    </div>
  );
}
