import { useEffect, useState } from "react";
import api, { errorMessage, unwrapList } from "../api";
import { useToast } from "../context/ToastContext";

export default function EntryExitPage() {
  const toast = useToast();
  const [vehicleId, setVehicleId] = useState("");
  const [info, setInfo] = useState(null);
  const [slots, setSlots] = useState([]);
  const [slotId, setSlotId] = useState("");
  const [preview, setPreview] = useState(null);

  async function loadSlots() {
    const { data } = await api.get("/parking-slots/");
    const list = unwrapList(data);
    setSlots(list.filter((s) => s.status === "AVAILABLE"));
  }

  useEffect(() => {
    loadSlots();
  }, []);

  async function lookup() {
    try {
      const { data } = await api.get(`/vehicles/${vehicleId.toUpperCase()}/`);
      setInfo(data);
      setPreview(null);
      if (data.status === "ACTIVE" || data.status === "RESERVED") {
        const prev = await api.get("/parking-records/preview/", { params: { vehicle_id: data.vehicle_id } });
        setPreview(prev.data);
      }
    } catch (err) {
      setInfo(null);
      toast.show(errorMessage(err), "error");
    }
  }

  async function parkAndEnter() {
    try {
      await api.post("/parking-records/park/", { vehicle_id: info.vehicle_id, slot_id: slotId });
      await api.post("/parking-records/entry/", { vehicle_id: info.vehicle_id });
      toast.show("Entry recorded");
      lookup();
      loadSlots();
    } catch (err) {
      toast.show(errorMessage(err), "error");
    }
  }

  async function enterOnly() {
    try {
      await api.post("/parking-records/entry/", { vehicle_id: info.vehicle_id, slot_id: slotId || undefined });
      toast.show("Entry recorded");
      lookup();
      loadSlots();
    } catch (err) {
      toast.show(errorMessage(err), "error");
    }
  }

  async function exitVehicle() {
    try {
      const { data } = await api.post("/parking-records/exit/", { vehicle_id: info.vehicle_id });
      toast.show(`Exited. Fee ${data.fee} BDT`);
      lookup();
      loadSlots();
    } catch (err) {
      toast.show(errorMessage(err), "error");
    }
  }

  async function pay() {
    try {
      await api.post("/payments/", { vehicle_id: info.vehicle_id });
      toast.show("Payment completed");
      lookup();
    } catch (err) {
      toast.show(errorMessage(err), "error");
    }
  }

  return (
    <div>
      <h1>Entry / Exit</h1>
      <div className="grid two">
        <div className="card">
          <h3>Lookup vehicle</h3>
          <div className="row">
            <input value={vehicleId} onChange={(e) => setVehicleId(e.target.value)} placeholder="CAR001" />
            <button className="btn" onClick={lookup}>Find</button>
          </div>
          {info && (
            <div style={{ marginTop: 16 }}>
              <p><b>Vehicle:</b> {info.vehicle_id} ({info.vehicle_type})</p>
              <p><b>Child:</b> {info.child_name} ({info.child})</p>
              <p><b>Guardian:</b> {info.guardian_name} ({info.guardian_id})</p>
              <p><b>Status:</b> {info.status} {info.current_slot ? `@ ${info.current_slot}` : ""}</p>
            </div>
          )}
        </div>
        <div className="card">
          <h3>Entry</h3>
          <p>Available slots: {slots.length}</p>
          <div className="field">
            <label>Assign slot</label>
            <select value={slotId} onChange={(e) => setSlotId(e.target.value)}>
              <option value="">Select slot</option>
              {slots.map((s) => (
                <option key={s.slot_id}>{s.slot_id}</option>
              ))}
            </select>
          </div>
          <div className="row">
            <button className="btn" disabled={!info} onClick={parkAndEnter}>Park + Entry</button>
            <button className="btn secondary" disabled={!info} onClick={enterOnly}>Entry only</button>
          </div>
        </div>
        <div className="card">
          <h3>Exit</h3>
          {preview ? (
            <>
              <p><b>Entry time:</b> {preview.entry_time ? new Date(preview.entry_time).toLocaleString() : "Reserved, not entered"}</p>
              <p><b>Current slot:</b> {preview.slot_id}</p>
              <p><b>Duration:</b> {preview.live_duration_minutes} min</p>
              <p><b>Calculated fee:</b> {preview.live_fee} BDT</p>
            </>
          ) : (
            <p>Lookup an active vehicle to preview fee.</p>
          )}
          <div className="row">
            <button className="btn" disabled={!info} onClick={exitVehicle}>Confirm Exit</button>
            <button className="btn secondary" disabled={!info} onClick={pay}>Payment</button>
          </div>
        </div>
      </div>
    </div>
  );
}
