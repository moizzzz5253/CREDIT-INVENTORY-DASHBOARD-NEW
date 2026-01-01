import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getStorageBoxesWithComponents } from "../../api/locations.api";

export default function StorageBoxList() {
  const navigate = useNavigate();
  const [storageBoxes, setStorageBoxes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStorageBoxes();
  }, []);

  const loadStorageBoxes = async () => {
    try {
      const data = await getStorageBoxesWithComponents();
      setStorageBoxes(data);
    } catch (error) {
      console.error("Failed to load storage boxes:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-8 text-zinc-400">Loading storage boxes...</div>
    );
  }

  return (
    <div className="space-y-4 sm:space-y-6 px-2 sm:px-0">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0">
        <h1 className="text-2xl sm:text-3xl font-bold text-white">Storage Boxes</h1>
        <button
          onClick={() => navigate("/locations")}
          className="px-3 sm:px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded text-white text-sm sm:text-base w-full sm:w-auto"
        >
          ← Back to Locations
        </button>
      </div>

      {storageBoxes.length === 0 ? (
        <div className="text-center text-zinc-400 py-8 text-sm sm:text-base">
          No storage boxes with components found.
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {storageBoxes.map((box) => (
            <div
              key={box.storage_box_index}
              onClick={() => navigate(`/locations/storage-box/${box.storage_box_index}`)}
              className="bg-zinc-800 border border-zinc-700 rounded-lg p-4 sm:p-6 cursor-pointer hover:border-blue-500 hover:shadow-lg transition-all"
            >
              <div className="flex items-center justify-between mb-3 sm:mb-4">
                <h2 className="text-xl sm:text-2xl font-bold text-white truncate pr-2">
                  Storage Box {box.storage_box_index}
                </h2>
                <div className="text-3xl sm:text-4xl flex-shrink-0">📦</div>
              </div>
              <p className="text-zinc-400 text-sm sm:text-base">
                {box.component_count} component{box.component_count !== 1 ? "s" : ""}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

