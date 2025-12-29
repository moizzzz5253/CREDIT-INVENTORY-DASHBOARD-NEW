import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export default function ComponentCard({ component, onModify, onDelete, onView }) {
  const [showActions, setShowActions] = useState(false);
  const navigate = useNavigate();

  const handleView = () => {
    if (onView) return onView(component);
    // Only navigate to container if it exists (CABINET storage with container)
    if (component.container?.code) {
      navigate(`/containers/${component.container.code}`);
    } else {
      // For drawers/storage boxes, or bare cabinet storage, just show alert
      alert(`Location: ${getLocationLabel(component)}`);
    }
  };

  // Get location label from API response
  const getLocationLabel = (component) => {
    // Use the location label from the API (already formatted correctly)
    if (component?.location?.label) {
      return component.location.label; // e.g. "Cabinet 1 Shelf 2 A2-b1", "Drawer 1", "Storage Box 1"
    }
    // Fallback for old data
    return component?.container?.code ?? "Unknown Location";
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
            Location: {getLocationLabel(component)}
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
