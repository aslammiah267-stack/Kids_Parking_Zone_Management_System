import { useEffect, useState } from "react";
import api, { errorMessage, unwrapList } from "../api";
import { useToast } from "../context/ToastContext";
import Modal from "../components/Modal";

export default function GuardiansPage() {
  const toast = useToast();
  const [rows, setRows] = useState([]);
  const [q, setQ] = useState("");
  const [form, setForm] = useState(null);
  const [view, setView] = useState(null);

  async function load() {
    const { data } = await api.get("/guardians/", { params: { search: q, page_size: 100 } });
    setRows(unwrapList(data));
  }

  useEffect(() => {
    load().catch((e) => toast.show(errorMessage(e), "error"));
  }, []);

  async function save(e) {
    e.preventDefault();
    try {
      if (form.mode === "edit") {
        await api.put(`/guardians/${form.guardian_id}/`, form);
      } else {
        await api.post("/guardians/", form);
      }
      toast.show("Guardian saved");
      setForm(null);
      load();
    } catch (err) {
      toast.show(errorMessage(err), "error");
    }
  }

  async function remove(id) {
    if (!confirm(`Delete guardian ${id}?`)) return;
    try {
      await api.delete(`/guardians/${id}/`);
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
          <h1>Guardians</h1>
          <p style={{ color: "#5b6b7c" }}>One guardian can have multiple children.</p>
        </div>
        <button className="btn" onClick={() => setForm({ mode: "create", guardian_id: "", name: "", phone: "" })}>
          Add guardian
        </button>
      </div>
      <div className="card">
        <div className="toolbar">
          <input placeholder="Search guardians" value={q} onChange={(e) => setQ(e.target.value)} />
          <button className="btn secondary" onClick={load}>
            Search
          </button>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Guardian ID</th>
                <th>Name</th>
                <th>Phone</th>
                <th>Children</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((g) => (
                <tr key={g.guardian_id}>
                  <td>{g.guardian_id}</td>
                  <td>{g.name}</td>
                  <td>{g.phone}</td>
                  <td>{g.children_count}</td>
                  <td className="row">
                    <button className="btn ghost" onClick={() => setView(g)}>View</button>
                    <button className="btn ghost" onClick={() => setForm({ ...g, mode: "edit" })}>Edit</button>
                    <button className="btn ghost" onClick={() => remove(g.guardian_id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!rows.length && <div className="empty">No guardians found.</div>}
        </div>
      </div>
      {form && (
        <Modal title={form.mode === "edit" ? "Edit guardian" : "Add guardian"} onClose={() => setForm(null)}>
          <form onSubmit={save}>
            <div className="field">
              <label>Guardian ID</label>
              <input value={form.guardian_id} disabled={form.mode === "edit"} onChange={(e) => setForm({ ...form, guardian_id: e.target.value.toUpperCase() })} required />
            </div>
            <div className="field">
              <label>Name</label>
              <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
            </div>
            <div className="field">
              <label>Phone</label>
              <input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} required />
            </div>
            <button className="btn">Save</button>
          </form>
        </Modal>
      )}
      {view && (
        <Modal title="Guardian details" onClose={() => setView(null)}>
          <p><b>ID:</b> {view.guardian_id}</p>
          <p><b>Name:</b> {view.name}</p>
          <p><b>Phone:</b> {view.phone}</p>
          <p><b>Children:</b> {view.children_count}</p>
        </Modal>
      )}
    </div>
  );
}
