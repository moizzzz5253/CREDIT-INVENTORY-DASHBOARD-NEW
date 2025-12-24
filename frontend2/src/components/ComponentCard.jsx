import { useState } from "react";
import { useNavigate } from "react-router-dom";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export default function ComponentCard({ component, onModify, onDelete, onView }) {
  const [showActions, setShowActions] = useState(false);
  const navigate = useNavigate();

  const handleView = () => {
    if (onView) return onView(component);
    navigate(`/containers/${component.container.code}`);
  };

  // ✅ CORRECT label logic based on ACTUAL API response
  const getContainerLabel = (component) => {
    if (component?.location?.label) {
      return component.location.label; // e.g. B3-b2
    }

    return component?.container?.code ?? "Unknown";
  };

  return (
    <div
      className="bg-zinc-800 border border-zinc-700 rounded-lg p-4 cursor-pointer hover:shadow-lg"
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
      onClick={() => setShowActions((s) => !s)}
    >
      <div className="flex items-center space-x-4">
        <img
          src={`${API_BASE}/${component.image_path}`}
          alt={component.name}
          className="w-24 h-24 object-cover rounded flex-shrink-0"
          onError={(e) => (e.currentTarget.src = "/placeholder.svg")}
        />

        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-white truncate text-xl">
            {component.name}
          </h4>

          <p className="text-zinc-400">{component.category}</p>
          <p className="text-zinc-300">Qty: {component.quantity}</p>
          <p className="text-zinc-300">
            Borrowed: {component.borrowed_quantity}
          </p>

          <p className="text-zinc-400 text-sm">
            Container: {getContainerLabel(component)}
          </p>

          {component.remarks && (
            <p className="text-zinc-400 text-xs mt-1">
              Remarks: {component.remarks}
            </p>
          )}
        </div>
      </div>

      {showActions && (
        <div className="mt-3 flex space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onModify && onModify(component);
            }}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-white"
          >
            Modify
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete && onDelete(component);
            }}
            className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-white"
          >
            Delete
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation();
              handleView();
            }}
            className="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 rounded text-white"
          >
            View Location
          </button>
        </div>
      )}
    </div>
  );
}
