import { useEffect, useState } from "react";
import api, { errorMessage, unwrapList } from "../api";
import { useToast } from "../context/ToastContext";
import Modal from "../components/Modal";

export default function SlotsPage() {
  const toast = useToast();
  const [slots, setSlots] = useState([]);
  const [selected, setSelected] = useState(null);
  const [newId, setNewId] = useState("");

  async function load() {
    const { data } = await api.get("/parking-slots/");
    setSlots(unwrapList(data));
  }

  useEffect(() => {
    load().catch((e) => toast.show(errorMessage(e), "error"));
  }, []);

  async function addSlot(e) {
    e.preventDefault();
    try {
      await api.post("/parking-slots/", { slot_id: newId.toUpperCase(), status: "AVAILABLE" });
      setNewId("");
      toast.show("Slot added");
      load();
    } catch (err) {
      toast.show(errorMessage(err), "error");
    }
  }

  return (
    <div>
      <div className="toolbar">
        <div>
          <h1>Parking Slots</h1>
          <p style={{ color: "#5b6b7c" }}>Click a slot to inspect occupancy details.</p>
        </div>
        <form className="row" onSubmit={addSlot}>
          <input placeholder="SLOT21" value={newId} onChange={(e) => setNewId(e.target.value)} required />
          <button className="btn">Add slot</button>
        </form>
      </div>
      <div className="slot-grid">
        {slots.map((s) => (
          <div key={s.slot_id} className={`slot ${s.status}`} onClick={() => setSelected(s)}>
            <h3>{s.slot_id}</h3>
            <span className={`badge ${s.status === "AVAILABLE" ? "ok" : "danger"}`}>{s.status}</span>
            {s.current_vehicle && <div style={{ marginTop: 8, fontSize: 13 }}>{s.current_vehicle}</div>}
          </div>
        ))}
      </div>
      {!slots.length && <div className="card empty">No slots yet.</div>}
      {selected && (
        <Modal title={selected.slot_id} onClose={() => setSelected(null)}>
          <p><b>Status:</b> {selected.status}</p>
          <p><b>Vehicle:</b> {selected.current_vehicle || "None"}</p>
          <p><b>Child:</b> {selected.current_child ? `${selected.current_child.name} (${selected.current_child.child_id})` : "—"}</p>
          <p><b>Guardian:</b> {selected.current_guardian ? `${selected.current_guardian.name} (${selected.current_guardian.phone})` : "—"}</p>
          <p><b>Entry time:</b> {selected.entry_time ? new Date(selected.entry_time).toLocaleString() : "—"}</p>
          <p><b>Duration:</b> {selected.duration_minutes ?? "—"} min</p>
        </Modal>
      )}
    </div>
  );
}
