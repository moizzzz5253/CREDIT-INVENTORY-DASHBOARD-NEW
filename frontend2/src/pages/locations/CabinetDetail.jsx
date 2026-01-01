import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getCabinetComponents } from "../../api/locations.api";
import ComponentCard from "../../components/ComponentCard";

export default function CabinetDetail() {
  const { cabinetNumber } = useParams();
  const navigate = useNavigate();
  const [cabinetData, setCabinetData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedShelf, setSelectedShelf] = useState(null);

  useEffect(() => {
    loadCabinetData();
  }, [cabinetNumber]);

  const loadCabinetData = async () => {
    try {
      const data = await getCabinetComponents(parseInt(cabinetNumber));
      setCabinetData(data);
      // Auto-select first shelf with components
      const shelfNumbers = Object.keys(data.shelves || {}).map(Number).sort();
      if (shelfNumbers.length > 0) {
        setSelectedShelf(shelfNumbers[0]);
      }
    } catch (error) {
      console.error("Failed to load cabinet data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-8 text-zinc-400">Loading cabinet...</div>
    );
  }

  if (!cabinetData) {
    return (
      <div className="text-center py-8 text-zinc-400">Cabinet not found.</div>
    );
  }

  const shelfNumbers = Object.keys(cabinetData.shelves || {}).map(Number).sort();

  return (
    <div className="space-y-4 sm:space-y-6 px-2 sm:px-0">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0">
        <h1 className="text-2xl sm:text-3xl font-bold text-white">
          Cabinet {cabinetNumber}
        </h1>
        <button
          onClick={() => navigate("/locations/cabinet")}
          className="px-3 sm:px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded text-white text-sm sm:text-base w-full sm:w-auto"
        >
          ← Back to Cabinets
        </button>
      </div>

      {/* Shelf Selector */}
      {shelfNumbers.length > 0 && (
        <div className="bg-zinc-800 border border-zinc-700 rounded-lg p-3 sm:p-4">
          <label className="text-zinc-400 text-xs sm:text-sm mb-2 block">Select Shelf:</label>
          <select
            value={selectedShelf || ""}
            onChange={(e) => setSelectedShelf(e.target.value ? parseInt(e.target.value) : null)}
            className="w-full sm:w-auto px-3 py-2 bg-zinc-900 border border-zinc-700 rounded text-white text-sm sm:text-base"
          >
            <option value="">All Shelves</option>
            {shelfNumbers.map((shelfNum) => (
              <option key={shelfNum} value={shelfNum}>
                Shelf {shelfNum === 0 ? "0 (No Shelf)" : shelfNum}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Display Shelves */}
      {selectedShelf !== null ? (
        // Show selected shelf only
        renderShelf(cabinetData.shelves[selectedShelf], selectedShelf, navigate, cabinetNumber)
      ) : (
        // Show all shelves
        shelfNumbers.map((shelfNum) => (
          <div key={shelfNum}>
            {renderShelf(cabinetData.shelves[shelfNum], shelfNum, navigate, cabinetNumber)}
          </div>
        ))
      )}
    </div>
  );
}

function renderShelf(shelfData, shelfNumber, navigate, cabinetNumber) {
  if (!shelfData) return null;

  return (
    <div key={shelfNumber} className="bg-zinc-800 border border-zinc-700 rounded-lg p-4 sm:p-6 mb-4 sm:mb-6">
      <h2 className="text-lg sm:text-xl font-bold text-white mb-3 sm:mb-4">
        Shelf {shelfNumber === 0 ? "0 (No Shelf)" : shelfNumber}
      </h2>

      {/* Containers on Shelf */}
      {shelfData.containers && shelfData.containers.length > 0 && (
        <div className="mb-4 sm:mb-6">
          <h3 className="text-base sm:text-lg font-semibold text-zinc-300 mb-2 sm:mb-3">Containers</h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2 sm:gap-4">
            {shelfData.containers.map((container) => (
              <div
                key={container.code}
                onClick={() =>
                  navigate(
                    `/locations/cabinet/${cabinetNumber}/shelf/${shelfNumber}/container/${container.code}`
                  )
                }
                className="bg-zinc-900 border border-zinc-700 rounded-lg p-2 sm:p-4 cursor-pointer hover:border-blue-500 transition"
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
          <h3 className="text-base sm:text-lg font-semibold text-zinc-300 mb-2 sm:mb-3">
            Components (Not in Container)
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
            {shelfData.bare_components.map((component) => (
              <ComponentCard key={component.id} component={component} />
            ))}
          </div>
        </div>
      )}

      {        (!shelfData.containers || shelfData.containers.length === 0) &&
        (!shelfData.bare_components || shelfData.bare_components.length === 0) && (
          <div className="text-zinc-400 text-center py-4 text-sm sm:text-base">
            No components on this shelf.
          </div>
        )}
    </div>
  );
}

