import api from "./axios";

export const getAllContainers = async () => {
  const res = await api.get("/containers");
  return res.data;
};

export const initContainers = async () => {
  const res = await api.post("/containers/init");
  return res.data;
};

export const regenerateQRCodes = async () => {
  const res = await api.post("/containers/regenerate-qr");
  return res.data;
};
