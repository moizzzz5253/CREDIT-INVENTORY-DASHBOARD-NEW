import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getShelfComponents } from "../../api/locations.api";
import ComponentCard from "../../components/ComponentCard";

export default function ShelfView() {
  const { cabinetNumber, shelfNumber } = useParams();
  const navigate = useNavigate();
  const [shelfData, setShelfData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadShelfData();
  }, [cabinetNumber, shelfNumber]);

  const loadShelfData = async () => {
    try {
      const data = await getShelfComponents(
        parseInt(cabinetNumber),
        parseInt(shelfNumber)
      );
      setShelfData(data);
    } catch (error) {
      console.error("Failed to load shelf data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-8 text-zinc-400">Loading shelf...</div>
    );
  }

  if (!shelfData) {
    return (
      <div className="text-center py-8 text-zinc-400">Shelf not found.</div>
    );
  }

  return (
    <div className="space-y-4 sm:space-y-6 px-2 sm:px-0">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0">
        <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-white break-words">
          Cabinet {cabinetNumber} - Shelf {shelfNumber === "0" ? "0 (No Shelf)" : shelfNumber}
        </h1>
        <button
          onClick={() => navigate(`/locations/cabinet/${cabinetNumber}`)}
          className="px-3 sm:px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded text-white text-sm sm:text-base w-full sm:w-auto"
        >
          ← Back to Cabinet
        </button>
      </div>

      {/* Containers */}
      {shelfData.containers && shelfData.containers.length > 0 && (
        <div>
          <h2 className="text-lg sm:text-xl font-bold text-white mb-3 sm:mb-4">Containers</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2 sm:gap-4">
            {shelfData.containers.map((container) => (
              <div
                key={container.code}
                onClick={() =>
                  navigate(
                    `/locations/cabinet/${cabinetNumber}/shelf/${shelfNumber}/container/${container.code}`
                  )
                }
                className="bg-zinc-800 border border-zinc-700 rounded-lg p-2 sm:p-4 cursor-pointer hover:border-blue-500 transition"
              >
                <div className="text-center">
                  <div className="text-lg sm:text-2xl font-bold text-white mb-1 sm:mb-2 break-all">
                    {container.code}
                  </div>
                  <div className="text-zinc-400 text-xs sm:text-sm">
                    {container.components.length} component{container.components.length !== 1 ? "s" : ""}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Bare Components */}
      {shelfData.bare_components && shelfData.bare_components.length > 0 && (
        <div>
          <h2 className="text-lg sm:text-xl font-bold text-white mb-3 sm:mb-4">
            Components (Not in Container)
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
            {shelfData.bare_components.map((component) => (
              <ComponentCard key={component.id} component={component} />
            ))}
          </div>
        </div>
      )}

      {(!shelfData.containers || shelfData.containers.length === 0) &&
        (!shelfData.bare_components || shelfData.bare_components.length === 0) && (
          <div className="text-zinc-400 text-center py-8 text-sm sm:text-base">
            No components on this shelf.
          </div>
        )}
    </div>
  );
}

