import React from "react";
import { useNavigate } from "react-router-dom";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export default function ContainerCard({ container }) {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate(`/containers/${container.code}`)}
      className="
        cursor-pointer
        bg-zinc-800
        rounded-lg
        p-4
        flex
        flex-col
        items-center
        justify-center
        border
        border-zinc-700
        hover:border-blue-500
        hover:scale-[1.02]
        transition
      "
    >
      <img
        src={`${API_BASE}/${container.qr_path}?t=${Date.now()}`}
        alt={container.code}
        className="w-40 h-40 object-contain mb-2"
        onError={(e) => {
          e.currentTarget.src = "/placeholder.png";
        }}
      />

      <span className="text-lg font-semibold text-white">
        {container.code}
      </span>
    </div>
  );
}
