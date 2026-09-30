import { createContext, useContext, useMemo, useState } from "react";

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const api = useMemo(
    () => ({
      show(message, type = "ok") {
        const id = crypto.randomUUID();
        setToasts((items) => [...items, { id, message, type }]);
        setTimeout(() => setToasts((items) => items.filter((t) => t.id !== id)), 3500);
      },
    }),
    []
  );
  return (
    <ToastContext.Provider value={api}>
      {children}
      <div className="toast-stack">
        {toasts.map((t) => (
          <div key={t.id} className={`toast ${t.type === "error" ? "error" : ""}`}>
            {t.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  return useContext(ToastContext);
}
