import axios from "axios";

const api = axios.create({
  baseURL: "http://192.168.100.37:8000", // FastAPI backend
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;
