import React, { useState, useEffect } from "react";

/**
 * DrawerVisualization - Visual representation of a drawer with opening animation
 * Shows components organized by location_type (NONE, BOX, PARTITION)
 */
export default function DrawerVisualization({ drawerData, onBoxClick, onPartitionClick }) {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    // Animate drawer opening
    const timer = setTimeout(() => setIsOpen(true), 100);
    return () => clearTimeout(timer);
  }, []);

  if (!drawerData) {
    return null;
  }

  return (
    <div
      className={`bg-zinc-900 border border-zinc-700 rounded-lg p-6 transition-all duration-500 ${
        isOpen ? "opacity-100" : "opacity-0"
      }`}
    >
      <div className="space-y-4">
        {/* Direct Components */}
        {drawerData.direct_components &&
          drawerData.direct_components.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">
                Direct Components ({drawerData.direct_components.length})
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                {drawerData.direct_components.slice(0, 8).map((comp) => (
                  <div
                    key={comp.id}
                    className="bg-zinc-800 border border-zinc-600 rounded p-2 text-center"
                  >
                    <div className="text-white text-sm font-semibold truncate">
                      {comp.name}
                    </div>
                    <div className="text-zinc-400 text-xs">Qty: {comp.quantity}</div>
                  </div>
                ))}
                {drawerData.direct_components.length > 8 && (
                  <div className="bg-zinc-800 border border-zinc-600 rounded p-2 text-center flex items-center justify-center">
                    <span className="text-zinc-400 text-sm">
                      +{drawerData.direct_components.length - 8} more
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

        {/* Boxes */}
        {drawerData.boxes && drawerData.boxes.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-white mb-2">
              Boxes ({drawerData.boxes.length})
            </h3>
            <div className="flex flex-wrap gap-2">
              {drawerData.boxes.map((box) => (
                <div
                  key={box.index}
                  onClick={() => onBoxClick && onBoxClick(box.index)}
                  className="bg-zinc-800 border border-zinc-600 rounded px-4 py-2 cursor-pointer hover:border-blue-500 hover:bg-zinc-700 transition"
                >
                  <div className="text-white font-semibold">Box {box.index}</div>
                  <div className="text-zinc-400 text-xs">
                    {box.components.length} component{box.components.length !== 1 ? "s" : ""}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Partitions Preview */}
        {drawerData.partitions && drawerData.partitions.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-white mb-2">
              Partitions ({drawerData.partitions.length})
            </h3>
            <div className="grid grid-cols-5 gap-1">
              {Array.from({ length: 25 }, (_, i) => i + 1).map((idx) => {
                const partition = drawerData.partitions.find((p) => p.index === idx);
                return (
                  <div
                    key={idx}
                    onClick={() => onPartitionClick && onPartitionClick(idx)}
                    className={`aspect-square border rounded text-xs flex items-center justify-center ${
                      partition
                        ? "bg-zinc-800 border-zinc-600 cursor-pointer hover:border-blue-500"
                        : "bg-zinc-900 border-zinc-700"
                    }`}
                  >
                    {partition ? (
                      <span className="text-white font-semibold">p{idx}</span>
                    ) : (
                      <span className="text-zinc-600">-</span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

