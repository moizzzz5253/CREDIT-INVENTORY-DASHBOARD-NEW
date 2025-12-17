import api from "./axios";

// Create component (multipart/form-data)
export const createComponent = async (formData) => {
  const res = await api.post("/components/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
};

// ✅ Get all components (for borrow dropdown)
export const getAllComponents = async () => {
  const res = await api.get("/components/");
  return res.data;
};
