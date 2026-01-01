import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getStorageBoxComponents } from "../../api/locations.api";
import ComponentCard from "../../components/ComponentCard";

export default function StorageBoxDetail() {
  const { boxIndex } = useParams();
  const navigate = useNavigate();
  const [components, setComponents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadComponents();
  }, [boxIndex]);

  const loadComponents = async () => {
    try {
      const data = await getStorageBoxComponents(parseInt(boxIndex));
      setComponents(data);
    } catch (error) {
      console.error("Failed to load storage box components:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-8 text-zinc-400">Loading storage box...</div>
    );
  }

  return (
    <div className="space-y-4 sm:space-y-6 px-2 sm:px-0">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0">
        <h1 className="text-2xl sm:text-3xl font-bold text-white">Storage Box {boxIndex}</h1>
        <button
          onClick={() => navigate("/locations/storage-box")}
          className="px-3 sm:px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded text-white text-sm sm:text-base w-full sm:w-auto"
        >
          ← Back to Storage Boxes
        </button>
      </div>

      {/* Visual Box Representation */}
      <div className="bg-zinc-800 border border-zinc-700 rounded-lg p-4 sm:p-6">
        <h2 className="text-lg sm:text-xl font-bold text-white mb-3 sm:mb-4">Components</h2>
        {components.length === 0 ? (
          <div className="text-zinc-400 text-center py-8 text-sm sm:text-base">
            No components in this storage box.
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3 sm:gap-4">
            {components.map((component) => (
              <ComponentCard key={component.id} component={component} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

