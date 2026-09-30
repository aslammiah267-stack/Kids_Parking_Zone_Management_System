import axios from "axios";

const api = axios.create({
  baseURL: "/api",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("kpzms_access");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function unwrapList(data) {
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.results)) return data.results;
  return [];
}

export function errorMessage(error) {
  const data = error?.response?.data;
  if (!data) return error.message || "Request failed";
  if (typeof data.message === "string") return data.message;
  if (typeof data.detail === "string") return data.detail;
  if (typeof data === "string") return data;
  return JSON.stringify(data.message || data.errors || data);
}

export default api;
