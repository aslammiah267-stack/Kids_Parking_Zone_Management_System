import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import ChildrenPage from "./pages/ChildrenPage";
import GuardiansPage from "./pages/GuardiansPage";
import VehiclesPage from "./pages/VehiclesPage";
import SlotsPage from "./pages/SlotsPage";
import EntryExitPage from "./pages/EntryExitPage";
import PaymentsPage from "./pages/PaymentsPage";
import HistoryPage from "./pages/HistoryPage";
import ReportsPage from "./pages/ReportsPage";
import CompilerPage from "./pages/CompilerPage";
import SettingsPage from "./pages/SettingsPage";

function Protected({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="center-screen">Loading session…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <Protected>
            <Layout />
          </Protected>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="children" element={<ChildrenPage />} />
        <Route path="guardians" element={<GuardiansPage />} />
        <Route path="vehicles" element={<VehiclesPage />} />
        <Route path="slots" element={<SlotsPage />} />
        <Route path="entry-exit" element={<EntryExitPage />} />
        <Route path="payments" element={<PaymentsPage />} />
        <Route path="history" element={<HistoryPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="compiler" element={<CompilerPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
