import api from "./axios";

// Initialize all containers (one-time)
export const initContainers = async () => {
  const res = await api.post("/containers/init");
  return res.data;
};

// Regenerate all QR codes safely
export const regenerateQRCodes = async () => {
  const res = await api.post("/containers/regenerate-qr");
  return res.data;
};

// Get all containers
export const getAllContainers = async () => {
  const res = await api.get("/containers/");
  return res.data;
};

// Get components inside a specific container
export const getComponentsInContainer = async (containerCode) => {
  const res = await api.get(`/containers/${containerCode}/components`);
  return res.data;
};
