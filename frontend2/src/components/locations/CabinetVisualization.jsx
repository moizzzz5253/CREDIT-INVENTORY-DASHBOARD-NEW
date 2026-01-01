import React from "react";

/**
 * CabinetVisualization - Visual representation of a cabinet with shelves
 * Shows shelves 1-5 and containers/components on each shelf
 */
export default function CabinetVisualization({ cabinetData, onShelfClick, onContainerClick }) {
  if (!cabinetData || !cabinetData.shelves) {
    return null;
  }

  const shelfNumbers = Object.keys(cabinetData.shelves)
    .map(Number)
    .sort((a, b) => a - b);

  return (
    <div className="bg-zinc-900 border border-zinc-700 rounded-lg p-6">
      <div className="flex flex-col gap-4">
        {shelfNumbers.map((shelfNum) => {
          const shelf = cabinetData.shelves[shelfNum];
          return (
            <div
              key={shelfNum}
              className="bg-zinc-800 border border-zinc-600 rounded p-4"
            >
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-white">
                  Shelf {shelfNum === 0 ? "0 (No Shelf)" : shelfNum}
                </h3>
                {onShelfClick && (
                  <button
                    onClick={() => onShelfClick(shelfNum)}
                    className="text-sm text-blue-400 hover:text-blue-300"
                  >
                    View Details →
                  </button>
                )}
              </div>

              {/* Containers on Shelf */}
              {shelf.containers && shelf.containers.length > 0 && (
                <div className="mb-3">
                  <div className="text-sm text-zinc-400 mb-2">Containers:</div>
                  <div className="flex flex-wrap gap-2">
                    {shelf.containers.map((container) => (
                      <div
                        key={container.code}
                        onClick={() => onContainerClick && onContainerClick(container.code)}
                        className="bg-zinc-700 border border-zinc-600 rounded px-3 py-2 cursor-pointer hover:border-blue-500 hover:bg-zinc-600 transition text-white font-semibold"
                      >
                        {container.code}
                        <span className="text-xs text-zinc-400 ml-2">
                          ({container.components.length})
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Bare Components */}
              {shelf.bare_components && shelf.bare_components.length > 0 && (
                <div>
                  <div className="text-sm text-zinc-400 mb-2">
                    Bare Components ({shelf.bare_components.length}):
                  </div>
                  <div className="text-zinc-300 text-sm">
                    {shelf.bare_components
                      .map((c) => c.name)
                      .slice(0, 3)
                      .join(", ")}
                    {shelf.bare_components.length > 3 && "..."}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

