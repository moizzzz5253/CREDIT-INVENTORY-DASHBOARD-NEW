import React, { useState } from "react";
import { X } from "lucide-react";

export default function PasswordPromptModal({ isOpen, onClose, onVerify, error }) {
  const [password, setPassword] = useState("");
  const [isVerifying, setIsVerifying] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!password.trim()) return;

    setIsVerifying(true);
    try {
      await onVerify(password);
      setPassword("");
    } catch (err) {
      // Error is handled by parent component
    } finally {
      setIsVerifying(false);
    }
  };

  const handleClose = () => {
    setPassword("");
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-zinc-800 rounded-lg p-6 w-full max-w-md border border-zinc-700">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-white">Admin Access</h2>
          <button
            onClick={handleClose}
            className="text-zinc-400 hover:text-white transition-colors"
            disabled={isVerifying}
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">
              Enter Admin Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 bg-zinc-900 border border-zinc-700 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter password"
              autoFocus
              disabled={isVerifying}
            />
          </div>

          {error && (
            <div className="bg-red-900/50 border border-red-600 text-red-300 px-4 py-2 rounded text-sm">
              {error}
            </div>
          )}

          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={handleClose}
              className="px-4 py-2 text-zinc-300 hover:text-white transition-colors"
              disabled={isVerifying}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={isVerifying || !password.trim()}
            >
              {isVerifying ? "Verifying..." : "Verify"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

