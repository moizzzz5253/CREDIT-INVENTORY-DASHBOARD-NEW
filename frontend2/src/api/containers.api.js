import api from "./axios";

export const getAllContainers = async (cabinetNumber = null) => {
  const params = cabinetNumber ? { cabinet_number: cabinetNumber } : {};
  const res = await api.get("/containers", { params });
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

export const getComponentsInContainer = async (containerCode, params = {}) => {
  const res = await api.get(`/containers/${containerCode}/components`, { params });
  return res.data;
};
