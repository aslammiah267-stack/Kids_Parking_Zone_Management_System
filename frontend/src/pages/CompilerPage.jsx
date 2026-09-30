import { useState } from "react";
import api, { errorMessage } from "../api";
import { useToast } from "../context/ToastContext";

const STAGES = ["INPUT", "LEXICAL_ANALYSIS", "TOKENS", "SYNTAX_ANALYSIS", "SEMANTIC_ANALYSIS", "INTERMEDIATE_CODE", "EXECUTION", "OUTPUT"];

const SAMPLE = `REGISTER CHILD101
REGISTER CAR101
PARK CAR101 SLOT05
ENTRY CAR101`;

export default function CompilerPage() {
  const toast = useToast();
  const [command, setCommand] = useState(SAMPLE);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    try {
      const { data } = await api.post("/compiler/execute/", { command });
      setResult(data);
      toast.show(data.success ? "Command executed" : data.error_type);
    } catch (err) {
      const data = err.response?.data;
      if (data && data.error_type) {
        setResult(data);
        toast.show(data.error_type, "error");
      } else {
        toast.show(errorMessage(err), "error");
      }
    } finally {
      setLoading(false);
    }
  }

  const completed = result?.stages_completed || [];
  const failed = result && !result.success;

  return (
    <div>
      <h1>KPCL Compiler</h1>
      <p style={{ color: "#5b6b7c" }}>Kids Parking Command Language — lexical, syntax, semantic, IR, and execution pipeline.</p>
      <div className="pipeline">
        {STAGES.map((stage) => {
          const done = completed.includes(stage);
          const isError = failed && !done && completed.length && STAGES.indexOf(stage) === completed.length;
          return (
            <span key={stage} className={`pipe ${done ? "done" : ""} ${isError ? "error" : ""}`}>
              {stage.replaceAll("_", " ")}
            </span>
          );
        })}
      </div>
      <div className="compiler-grid">
        <div className="card">
          <h3>Command Editor</h3>
          <textarea className="editor" value={command} onChange={(e) => setCommand(e.target.value)} />
          <div className="row" style={{ marginTop: 12 }}>
            <button className="btn" onClick={run} disabled={loading}>{loading ? "Running…" : "RUN"}</button>
            <button className="btn secondary" onClick={() => { setCommand(""); setResult(null); }}>CLEAR</button>
          </div>
        </div>
        <div className="card">
          <h3>Tokens</h3>
          <table>
            <thead>
              <tr><th>TOKEN</th><th>LEXEME</th><th>TYPE</th></tr>
            </thead>
            <tbody>
              {(result?.tokens || []).map((t, i) => (
                <tr key={i}>
                  <td>{t.lexeme}</td>
                  <td>{t.lexeme}</td>
                  <td>{t.token_type}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!result?.tokens?.length && <div className="empty">Run a command to see tokens.</div>}
        </div>
        <div className="card">
          <h3>Syntax Analysis</h3>
          <p>Syntax: <b>{result ? (result.syntax_valid ? "VALID" : "INVALID") : "—"}</b></p>
          <h3>Semantic Analysis</h3>
          <p>Semantic: <b>{result ? (result.semantic_valid ? "VALID" : "INVALID") : "—"}</b></p>
          {result?.error_type && (
            <p style={{ color: "#be123c" }}>
              {result.error_type}: {result.message}
            </p>
          )}
        </div>
        <div className="card">
          <h3>Intermediate Code</h3>
          <pre>
            {(result?.intermediate_code || []).map((ins) => `${ins.instruction} ${ins.operand ?? ""}`).join("\n") || "—"}
          </pre>
          <h3>Execution Result</h3>
          <p>{result?.result || result?.message || "—"}</p>
          {result?.results && (
            <ol>
              {result.results.map((r, i) => (
                <li key={i}>{r.command}: {r.success ? r.result : `${r.error_type} — ${r.message}`}</li>
              ))}
            </ol>
          )}
        </div>
      </div>
    </div>
  );
}
