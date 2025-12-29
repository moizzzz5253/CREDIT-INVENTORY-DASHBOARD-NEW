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
  
  // Storage location fields
  form.append("storage_type", payload.storage_type || "CABINET");
  
  if (payload.storage_type === "CABINET") {
    if (payload.cabinet_number) form.append("cabinet_number", payload.cabinet_number);
    if (payload.shelf_number !== undefined) form.append("shelf_number", payload.shelf_number);
    if (payload.container_id) form.append("container_id", payload.container_id);
  } else if (payload.storage_type === "DRAWER") {
    if (payload.drawer_index) form.append("drawer_index", payload.drawer_index);
  } else if (payload.storage_type === "STORAGE_BOX") {
    if (payload.storage_box_index) form.append("storage_box_index", payload.storage_box_index);
  }
  
  // Box/Partition location (for containers/drawers)
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
  
  // Storage location fields
  if (payload.storage_type) form.append("storage_type", payload.storage_type);
  
  // Only send fields that are explicitly set (not undefined/null)
  // The backend will clear incompatible fields when storage_type changes
  if (payload.cabinet_number !== undefined && payload.cabinet_number !== null) {
    form.append("cabinet_number", payload.cabinet_number);
  }
  if (payload.shelf_number !== undefined && payload.shelf_number !== null) {
    form.append("shelf_number", payload.shelf_number);
  }
  if (payload.container_id !== undefined && payload.container_id !== null) {
    form.append("container_id", payload.container_id);
  }
  if (payload.drawer_index !== undefined && payload.drawer_index !== null) {
    form.append("drawer_index", payload.drawer_index);
  }
  if (payload.storage_box_index !== undefined && payload.storage_box_index !== null) {
    form.append("storage_box_index", payload.storage_box_index);
  }
  
  // Box/Partition location
  if (payload.location_type) form.append("location_type", payload.location_type);
  if (payload.location_index !== undefined && payload.location_index !== null) form.append("location_index", payload.location_index);
  
  if (payload.remarks !== undefined) form.append("remarks", payload.remarks);
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
