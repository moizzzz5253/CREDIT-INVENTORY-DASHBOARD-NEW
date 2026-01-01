import React, { useEffect, useState } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import { getDrawerComponents } from "../../api/locations.api";
import ComponentCard from "../../components/ComponentCard";

export default function DrawerDetail() {
  const { drawerIndex } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [drawerData, setDrawerData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedBox, setSelectedBox] = useState(null);
  const [selectedPartition, setSelectedPartition] = useState(null);

  useEffect(() => {
    loadDrawerData();
  }, [drawerIndex]);

  useEffect(() => {
    // Handle deep linking from query params
    const boxParam = searchParams.get("box");
    const partitionParam = searchParams.get("partition");
    if (boxParam) {
      setSelectedBox(parseInt(boxParam));
      setSelectedPartition(null);
    } else if (partitionParam) {
      setSelectedPartition(parseInt(partitionParam));
      setSelectedBox(null);
    }
  }, [searchParams]);

  const loadDrawerData = async () => {
    try {
      const data = await getDrawerComponents(parseInt(drawerIndex));
      setDrawerData(data);
    } catch (error) {
      console.error("Failed to load drawer data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-8 text-zinc-400">Loading drawer...</div>
    );
  }

  if (!drawerData) {
    return (
      <div className="text-center py-8 text-zinc-400">Drawer not found.</div>
    );
  }

  return (
    <div className="space-y-4 sm:space-y-6 px-2 sm:px-0">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0">
        <h1 className="text-2xl sm:text-3xl font-bold text-white">Drawer {drawerIndex}</h1>
        <button
          onClick={() => navigate("/locations/drawer")}
          className="px-3 sm:px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded text-white text-sm sm:text-base w-full sm:w-auto"
        >
          ← Back to Drawers
        </button>
      </div>

      {/* Direct Components */}
      {drawerData.direct_components && drawerData.direct_components.length > 0 && (
        <div>
          <h2 className="text-lg sm:text-xl font-bold text-white mb-3 sm:mb-4">Direct Components</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
            {drawerData.direct_components.map((component) => (
              <ComponentCard key={component.id} component={component} />
            ))}
          </div>
        </div>
      )}

      {/* Boxes */}
      {drawerData.boxes && drawerData.boxes.length > 0 && (
        <div>
          <h2 className="text-lg sm:text-xl font-bold text-white mb-3 sm:mb-4">Boxes</h2>
          <select
            value={selectedBox || ""}
            onChange={(e) => {
              const boxIdx = e.target.value ? parseInt(e.target.value) : null;
              setSelectedBox(boxIdx);
              setSelectedPartition(null);
              if (boxIdx) {
                navigate(`/locations/drawer/${drawerIndex}?box=${boxIdx}`);
              } else {
                navigate(`/locations/drawer/${drawerIndex}`);
              }
            }}
            className="w-full sm:w-auto px-3 py-2 bg-zinc-900 border border-zinc-700 rounded text-white mb-3 sm:mb-4 text-sm sm:text-base"
          >
            <option value="">Select a box...</option>
            {drawerData.boxes.map((box) => (
              <option key={box.index} value={box.index}>
                Box {box.index}
              </option>
            ))}
          </select>

          {selectedBox !== null && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
              {drawerData.boxes
                .find((b) => b.index === selectedBox)
                ?.components.map((component) => (
                  <ComponentCard key={component.id} component={component} />
                ))}
            </div>
          )}
        </div>
      )}

      {/* Partitions */}
      {drawerData.partitions && drawerData.partitions.length > 0 && (
        <div>
          <h2 className="text-lg sm:text-xl font-bold text-white mb-3 sm:mb-4">Partitions</h2>
          <div className="grid gap-1 sm:gap-2 overflow-x-auto" style={{ gridTemplateColumns: "repeat(5, minmax(0, 1fr))" }}>
            {Array.from({ length: 25 }, (_, i) => i + 1).map((partitionIndex) => {
              const partition = drawerData.partitions.find(
                (p) => p.index === partitionIndex
              );
              const isSelected = selectedPartition === partitionIndex;

              return (
                <div
                  key={partitionIndex}
                  onClick={() => {
                    setSelectedPartition(partitionIndex);
                    setSelectedBox(null);
                    navigate(`/locations/drawer/${drawerIndex}?partition=${partitionIndex}`);
                  }}
                  className={`aspect-square border rounded flex flex-col items-center justify-center p-0.5 sm:p-1 bg-zinc-800 relative overflow-hidden min-w-[40px] sm:min-w-0 ${
                    partition
                      ? "cursor-pointer hover:border-blue-500 hover:shadow-lg transition-all border-zinc-600"
                      : "border-zinc-700"
                  } ${isSelected ? "border-blue-500 ring-2 ring-blue-500" : ""}`}
                >
                  <div className="absolute top-0.5 left-0.5 text-white text-[10px] sm:text-xs font-bold bg-zinc-700 bg-opacity-80 px-0.5 sm:px-1 rounded z-10">
                    p{partitionIndex}
                  </div>
                  {partition ? (
                    <div className="w-full h-full">
                      <ComponentCard compact component={partition.components[0]} />
                    </div>
                  ) : (
                    <span className="text-zinc-500 text-xs">Empty</span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {        (!drawerData.direct_components || drawerData.direct_components.length === 0) &&
        (!drawerData.boxes || drawerData.boxes.length === 0) &&
        (!drawerData.partitions || drawerData.partitions.length === 0) && (
          <div className="text-zinc-400 text-center py-8 text-sm sm:text-base">
            No components in this drawer.
          </div>
        )}
    </div>
  );
}

