import { useState } from "react";
import { deleteComponent } from "../../api/components.api";

export default function DeleteComponentModal({
  component,
  onClose,
  onDeleted,
}) {
  const [reason, setReason] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleDelete = async () => {
    if (!reason.trim()) {
      setError("Delete reason is required");
      return;
    }

    try {
      setLoading(true);
      await deleteComponent(component.id, reason);
      onDeleted();
      onClose();
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to delete component"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
      <div className="bg-zinc-900 p-6 rounded w-full max-w-md">
        <h2 className="text-lg font-semibold mb-3 text-red-400">
          Delete Component
        </h2>

        <div className="mb-3">
          <div className="font-medium">{component.name}</div>
          <div className="text-sm text-zinc-400">
            Category: {component.category}
          </div>
          <div className="text-sm">
            Quantity: {component.quantity}
          </div>
        </div>

        <textarea
          className="w-full bg-zinc-800 p-2 rounded mb-2"
          placeholder="Reason for deleting this component..."
          value={reason}
          onChange={(e) => setReason(e.target.value)}
        />

        {error && (
          <div className="text-red-400 text-sm mb-2">
            {error}
          </div>
        )}

        <div className="flex justify-end gap-3 mt-4">
          <button
            className="px-4 py-2 bg-zinc-700 rounded"
            onClick={onClose}
            disabled={loading}
          >
            Cancel
          </button>

          <button
            className="px-4 py-2 bg-red-600 rounded"
            onClick={handleDelete}
            disabled={loading}
          >
            {loading ? "Deleting..." : "Delete"}
          </button>
        </div>
      </div>
    </div>
  );
}
