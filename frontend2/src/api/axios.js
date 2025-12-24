import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL ?? "http://192.168.100.37:8000";

const api = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;
