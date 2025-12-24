import api from "./axios";

export const getDashboardStats = async () => {
  const res = await api.get("/reports/stats");
  return res.data;
};