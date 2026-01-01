import api from "./axios";

// --------------------------------------------------
// CABINET ENDPOINTS
// --------------------------------------------------

export const getCabinetsWithComponents = async () => {
  const res = await api.get("/locations/cabinets");
  return res.data;
};

export const getCabinetComponents = async (cabinetNumber) => {
  const res = await api.get(`/locations/cabinets/${cabinetNumber}`);
  return res.data;
};

export const getShelfComponents = async (cabinetNumber, shelfNumber) => {
  const res = await api.get(`/locations/cabinets/${cabinetNumber}/shelves/${shelfNumber}`);
  return res.data;
};

// --------------------------------------------------
// DRAWER ENDPOINTS
// --------------------------------------------------

export const getDrawersWithComponents = async () => {
  const res = await api.get("/locations/drawers");
  return res.data;
};

export const getDrawerComponents = async (drawerIndex) => {
  const res = await api.get(`/locations/drawers/${drawerIndex}`);
  return res.data;
};

// --------------------------------------------------
// STORAGE BOX ENDPOINTS
// --------------------------------------------------

export const getStorageBoxesWithComponents = async () => {
  const res = await api.get("/locations/storage-boxes");
  return res.data;
};

export const getStorageBoxComponents = async (boxIndex) => {
  const res = await api.get(`/locations/storage-boxes/${boxIndex}`);
  return res.data;
};

