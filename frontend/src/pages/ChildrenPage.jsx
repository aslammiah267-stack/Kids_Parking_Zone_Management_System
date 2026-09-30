import { useEffect, useState } from "react";
import api, { errorMessage, unwrapList } from "../api";
import { useToast } from "../context/ToastContext";
import Modal from "../components/Modal";

export default function ChildrenPage() {
  const toast = useToast();
  const [rows, setRows] = useState([]);
  const [guardians, setGuardians] = useState([]);
  const [q, setQ] = useState("");
  const [form, setForm] = useState(null);
  const [view, setView] = useState(null);

  async function load() {
    const [children, guards] = await Promise.all([
      api.get("/children/", { params: { search: q, page_size: 100 } }),
      api.get("/guardians/", { params: { page_size: 100 } }),
    ]);
    setRows(unwrapList(children.data));
    setGuardians(unwrapList(guards.data));
  }

  useEffect(() => {
    load().catch((e) => toast.show(errorMessage(e), "error"));
  }, []);

  async function save(e) {
    e.preventDefault();
    try {
      const payload = { child_id: form.child_id, name: form.name, age: Number(form.age), guardian: form.guardian };
      if (form.mode === "edit") await api.put(`/children/${form.child_id}/`, payload);
      else await api.post("/children/", payload);
      toast.show("Child saved");
      setForm(null);
      load();
    } catch (err) {
      toast.show(errorMessage(err), "error");
    }
  }

  async function remove(id) {
    if (!confirm(`Delete child ${id}?`)) return;
    try {
      await api.delete(`/children/${id}/`);
      toast.show("Deleted");
      load();
    } catch (err) {
      toast.show(errorMessage(err), "error");
    }
  }

  return (
    <div>
      <div className="toolbar">
        <div>
          <h1>Children</h1>
          <p style={{ color: "#5b6b7c" }}>Register children linked to a guardian.</p>
        </div>
        <button className="btn" onClick={() => setForm({ mode: "create", child_id: "", name: "", age: 6, guardian: guardians[0]?.guardian_id || "" })}>
          Add child
        </button>
      </div>
      <div className="card">
        <div className="toolbar">
          <input placeholder="Search children" value={q} onChange={(e) => setQ(e.target.value)} />
          <button className="btn secondary" onClick={load}>Search</button>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Child ID</th>
                <th>Name</th>
                <th>Age</th>
                <th>Guardian</th>
                <th>Created At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((c) => (
                <tr key={c.child_id}>
                  <td>{c.child_id}</td>
                  <td>{c.name}</td>
                  <td>{c.age}</td>
                  <td>{c.guardian_name} ({c.guardian})</td>
                  <td>{new Date(c.created_at).toLocaleString()}</td>
                  <td className="row">
                    <button className="btn ghost" onClick={() => setView(c)}>View</button>
                    <button className="btn ghost" onClick={() => setForm({ ...c, mode: "edit" })}>Edit</button>
                    <button className="btn ghost" onClick={() => remove(c.child_id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!rows.length && <div className="empty">No children found.</div>}
        </div>
      </div>
      {form && (
        <Modal title={form.mode === "edit" ? "Edit child" : "Add child"} onClose={() => setForm(null)}>
          <form onSubmit={save}>
            <div className="field">
              <label>Child ID</label>
              <input value={form.child_id} disabled={form.mode === "edit"} onChange={(e) => setForm({ ...form, child_id: e.target.value.toUpperCase() })} required />
            </div>
            <div className="field">
              <label>Name</label>
              <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
            </div>
            <div className="field">
              <label>Age</label>
              <input type="number" min="1" max="16" value={form.age} onChange={(e) => setForm({ ...form, age: e.target.value })} required />
            </div>
            <div className="field">
              <label>Guardian</label>
              <select value={form.guardian} onChange={(e) => setForm({ ...form, guardian: e.target.value })} required>
                <option value="">Select guardian</option>
                {guardians.map((g) => (
                  <option key={g.guardian_id} value={g.guardian_id}>{g.guardian_id} — {g.name}</option>
                ))}
              </select>
            </div>
            <button className="btn">Save</button>
          </form>
        </Modal>
      )}
      {view && (
        <Modal title="Child details" onClose={() => setView(null)}>
          <p><b>ID:</b> {view.child_id}</p>
          <p><b>Name:</b> {view.name}</p>
          <p><b>Age:</b> {view.age}</p>
          <p><b>Guardian:</b> {view.guardian_name} ({view.guardian})</p>
          <p><b>Phone:</b> {view.guardian_phone}</p>
        </Modal>
      )}
    </div>
  );
}
