import api from "./axios";

export const getAllComponents = async () => {
  const res = await api.get("/components");
  return res.data;
};

export const getComponentById = async (id) => {
  const res = await api.get(`/components/${id}`);
  return res.data;
};

export const createComponent = async (payload) => {
  const form = new FormData();
  form.append("name", payload.name);
  form.append("category", payload.category);
  form.append("quantity", payload.quantity);
  form.append("container_id", payload.container_id);
  form.append("location_type", payload.location_type ?? "NONE");
  if (payload.location_index) form.append("location_index", payload.location_index);
  if (payload.remarks) form.append("remarks", payload.remarks);
  if (payload.image) form.append("image", payload.image);

  const res = await api.post("/components/", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return res.data;
};

export const updateComponent = async (id, payload) => {
  const form = new FormData();
  if (payload.name) form.append("name", payload.name);
  if (payload.category) form.append("category", payload.category);
  if (payload.quantity !== undefined) form.append("quantity", payload.quantity);
  if (payload.container_id) form.append("container_id", payload.container_id);
  if (payload.location_type) form.append("location_type", payload.location_type);
  if (payload.location_index) form.append("location_index", payload.location_index);
  if (payload.remarks) form.append("remarks", payload.remarks);
  if (payload.image) form.append("image", payload.image);

  const res = await api.put(`/components/${id}`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return res.data;
};

export const deleteComponent = async (id, reason = "deleted") => {
  const res = await api.post(`/components/${id}/delete`, { reason });
  return res.data;
};

export const getCategories = async () => {
  const res = await api.get("/constants/categories");
  return res.data.categories || [];
};
