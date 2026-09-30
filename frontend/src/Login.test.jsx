import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Login from "./pages/Login";
import { AuthProvider } from "./context/AuthContext";
import { ToastProvider } from "./context/ToastContext";

test("login form renders credentials fields", () => {
  render(
    <MemoryRouter>
      <ToastProvider>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </ToastProvider>
    </MemoryRouter>
  );
  expect(screen.getByText("Kids Parking Zone")).toBeTruthy();
  expect(screen.getByDisplayValue("admin")).toBeTruthy();
});
