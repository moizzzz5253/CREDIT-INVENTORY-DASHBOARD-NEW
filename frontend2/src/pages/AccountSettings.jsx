import React, { useState, useEffect } from "react";
import { getAdminInfo, updateAdminInfo } from "../api/admin.api";

export default function AccountSettings() {
  const [adminInfo, setAdminInfo] = useState({
    name: "",
    email: "",
    email2: "",
    phone: "",
    has_custom_password: false,
  });
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    email2: "",
    phone: "",
    new_password: "",
    confirm_password: "",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState(""); // 'success' or 'error'

  useEffect(() => {
    loadAdminInfo();
  }, []);

  const loadAdminInfo = async () => {
    try {
      setLoading(true);
      const info = await getAdminInfo();
      setAdminInfo(info);
      setFormData({
        name: info.name || "",
        email: info.email || "",
        email2: info.email2 || "",
        phone: info.phone || "",
        new_password: "",
        confirm_password: "",
      });
    } catch (error) {
      setMessage("Failed to load admin information");
      setMessageType("error");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate password if provided
    if (formData.new_password) {
      if (formData.new_password.length < 6) {
        setMessage("Password must be at least 6 characters long");
        setMessageType("error");
        return;
      }
      if (formData.new_password !== formData.confirm_password) {
        setMessage("Passwords do not match");
        setMessageType("error");
        return;
      }
    }

    setSaving(true);
    setMessage("");
    setMessageType("");

    try {
      const updatePayload = {};
      if (formData.name) updatePayload.name = formData.name;
      if (formData.email) updatePayload.email = formData.email;
      if (formData.email2) updatePayload.email2 = formData.email2;
      if (formData.phone) updatePayload.phone = formData.phone;
      if (formData.new_password) updatePayload.new_password = formData.new_password;

      const updated = await updateAdminInfo(updatePayload);
      setAdminInfo(updated);
      setFormData((prev) => ({
        ...prev,
        new_password: "",
        confirm_password: "",
      }));
      setMessage("Account settings updated successfully!");
      setMessageType("success");
    } catch (error) {
      setMessage(
        error.response?.data?.detail || "Failed to update account settings"
      );
      setMessageType("error");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-zinc-400">Loading...</div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Account Settings</h1>
        <p className="text-zinc-400">
          Manage your admin account information and password
        </p>
      </div>

      {/* Password Status */}
      <div
        className={`p-4 rounded-lg border ${
          adminInfo.has_custom_password
            ? "bg-green-900/30 border-green-600"
            : "bg-yellow-900/30 border-yellow-600"
        }`}
      >
        <p className="text-sm">
          {adminInfo.has_custom_password ? (
            <span className="text-green-300">
              ✓ Using custom password
            </span>
          ) : (
            <span className="text-yellow-300">
              ⚠ Using default password. Please set a custom password for security.
            </span>
          )}
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="bg-zinc-900 p-6 rounded-lg border border-zinc-800 space-y-6">
        {/* Name */}
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">
            Name
          </label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter your name"
          />
        </div>

        {/* Email */}
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">
            Email
          </label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter your email"
          />
        </div>

        {/* Second Email */}
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">
            Enter 2nd email
          </label>
          <input
            type="email"
            name="email2"
            value={formData.email2}
            onChange={handleInputChange}
            className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter 2nd email"
          />
        </div>

        {/* Phone */}
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">
            Phone Number
          </label>
          <input
            type="tel"
            name="phone"
            value={formData.phone}
            onChange={handleInputChange}
            className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter your phone number"
          />
        </div>

        {/* Password Section */}
        <div className="border-t border-zinc-700 pt-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            Change Password
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">
                New Password
              </label>
              <input
                type="password"
                name="new_password"
                value={formData.new_password}
                onChange={handleInputChange}
                className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter new password (min 6 characters)"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">
                Confirm Password
              </label>
              <input
                type="password"
                name="confirm_password"
                value={formData.confirm_password}
                onChange={handleInputChange}
                className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Confirm new password"
              />
            </div>
            <p className="text-xs text-zinc-400">
              Leave password fields empty if you don't want to change the password
            </p>
          </div>
        </div>

        {/* Message */}
        {message && (
          <div
            className={`p-4 rounded-lg ${
              messageType === "success"
                ? "bg-green-600 text-white"
                : "bg-red-600 text-white"
            }`}
          >
            {message}
          </div>
        )}

        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </form>
    </div>
  );
}

