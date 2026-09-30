import { useEffect, useState } from "react";
import api, { errorMessage } from "../api";
import { useToast } from "../context/ToastContext";
import { useAuth } from "../context/AuthContext";

export default function SettingsPage() {
  const toast = useToast();
  const { user } = useAuth();
  const [form, setForm] = useState(null);

  useEffect(() => {
    api.get("/settings/parking/")
      .then((res) => setForm(res.data))
      .catch((e) => toast.show(errorMessage(e), "error"));
  }, []);

  async function save(e) {
    e.preventDefault();
    try {
      const { data } = await api.put("/settings/parking/", form);
      setForm(data);
      toast.show("Fee settings updated");
    } catch (err) {
      toast.show(errorMessage(err), "error");
    }
  }

  if (!form) return <div className="card">Loading settings…</div>;

  return (
    <div>
      <h1>Settings</h1>
      <div className="card" style={{ maxWidth: 520 }}>
        <h3>Parking fee configuration</h3>
        <p>First block = 20 BDT for 30 minutes. Extra block = 10 BDT per 30 minutes. Admins can change these rates.</p>
        <form onSubmit={save}>
          <div className="field">
            <label>First block minutes</label>
            <input type="number" value={form.first_block_minutes} onChange={(e) => setForm({ ...form, first_block_minutes: e.target.value })} />
          </div>
          <div className="field">
            <label>First block fee (BDT)</label>
            <input type="number" value={form.first_block_fee} onChange={(e) => setForm({ ...form, first_block_fee: e.target.value })} />
          </div>
          <div className="field">
            <label>Extra block minutes</label>
            <input type="number" value={form.extra_block_minutes} onChange={(e) => setForm({ ...form, extra_block_minutes: e.target.value })} />
          </div>
          <div className="field">
            <label>Extra block fee (BDT)</label>
            <input type="number" value={form.extra_block_fee} onChange={(e) => setForm({ ...form, extra_block_fee: e.target.value })} />
          </div>
          <button className="btn" disabled={user?.role !== "ADMIN"}>Save rates</button>
          {user?.role !== "ADMIN" && <p>Only administrators can change rates.</p>}
        </form>
      </div>
    </div>
  );
}
