import api from "./axios.js";

/**
 * Verify admin password
 * @param {string} password - The password to verify
 * @returns {Promise<{success: boolean, message: string}>}
 */
export const verifyAdminPassword = async (password) => {
  const response = await api.post("/api/admin/verify-password", {
    password,
  });
  return response.data;
};

/**
 * Get admin information
 * @returns {Promise<{name: string|null, email: string|null, phone: string|null, has_custom_password: boolean}>}
 */
export const getAdminInfo = async () => {
  const response = await api.get("/api/admin/info");
  return response.data;
};

/**
 * Update admin information
 * @param {Object} updateData - Admin update data
 * @param {string} [updateData.name] - Admin name
 * @param {string} [updateData.email] - Admin email
 * @param {string} [updateData.phone] - Admin phone
 * @param {string} [updateData.new_password] - New password
 * @returns {Promise<{name: string|null, email: string|null, phone: string|null, has_custom_password: boolean}>}
 */
export const updateAdminInfo = async (updateData) => {
  const response = await api.put("/api/admin/update", updateData);
  return response.data;
};

