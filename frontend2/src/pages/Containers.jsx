import { useEffect, useState } from "react";
import DashboardLayout from "../layouts/DashboardLayout";
import {
  getAllContainers,
  initContainers,
  regenerateQRCodes,
} from "../api/containers.api";

const API_BASE = "http://localhost:8000"; // backend base



export default function Containers() {
  const [containers, setContainers] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadContainers = async () => {
    setLoading(true);
    try {
      const data = await getAllContainers();
      setContainers(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadContainers();
  }, []);

  useEffect(() => {
  console.log("Containers API response:", containers);
  
}, [containers]);


  const handleInit = async () => {
    await initContainers();
    loadContainers();
  };

  const handleRegenerateQR = async () => {
    await regenerateQRCodes();
    loadContainers();
  };
  

  return (
    <DashboardLayout title="Containers">
      {/* Top controls */}
      <div className="flex flex-wrap gap-3 mb-6">
        <input
          type="text"
          placeholder="Search container..."
          className="px-3 py-2 rounded bg-zinc-800 border border-zinc-700"
        />

        <button
          onClick={handleInit}
          className="px-4 py-2 bg-blue-600 rounded"
        >
          Init Containers
        </button>

        <button
          onClick={handleRegenerateQR}
          className="px-4 py-2 bg-orange-600 rounded"
        >
          Regenerate QR Codes
        </button>
      </div>

      {/* Container grid */}
      {loading ? (
        <div>Loading containers…</div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-6">
          {containers.map((c) => (
            <div
              key={c.id}
              className="bg-zinc-900 border border-zinc-700 rounded-lg p-3 flex flex-col items-center cursor-pointer hover:border-blue-500 transition"
            >
              <img
                src={`${API_BASE}/${c.qr_path}`}
                alt={`QR ${c.code}`}
                className="w-32 h-32 object-contain bg-white p-1 rounded"
              />

              <div className="mt-2 font-semibold text-lg">{c.code}</div>
            </div>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
}
