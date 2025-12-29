import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import PasswordPromptModal from "./PasswordPromptModal";
import { verifyAdminPassword } from "../api/admin.api";

export default function ProtectedRoute({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(true);
  const [passwordError, setPasswordError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    // Show password modal on mount
    setShowPasswordModal(true);
  }, []);

  const handlePasswordVerify = async (password) => {
    try {
      const result = await verifyAdminPassword(password);
      if (result.success) {
        setIsAuthenticated(true);
        setShowPasswordModal(false);
        setPasswordError("");
      } else {
        setPasswordError(result.message || "Invalid password");
      }
    } catch (error) {
      setPasswordError(
        error.response?.data?.detail || "Failed to verify password"
      );
    }
  };

  const handleCloseModal = () => {
    // If user closes modal without authenticating, redirect to dashboard
    navigate("/dashboard");
  };

  if (!isAuthenticated) {
    return (
      <PasswordPromptModal
        isOpen={showPasswordModal}
        onClose={handleCloseModal}
        onVerify={handlePasswordVerify}
        error={passwordError}
      />
    );
  }

  return children;
}

