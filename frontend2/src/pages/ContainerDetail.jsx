import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getComponentsInContainer } from "../api/containers.api";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export default function ContainerDetail() {
  const { code } = useParams();
  const navigate = useNavigate();
  const [components, setComponents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedBox, setSelectedBox] = useState(null);
  const [selectedComponent, setSelectedComponent] = useState(null);

  useEffect(() => {
    loadComponents();
  }, [code]);

  const loadComponents = async () => {
    try {
      const data = await getComponentsInContainer(code);
      setComponents(data);
    } catch (error) {
      console.error("Failed to load components:", error);
    } finally {
      setLoading(false);
    }
  };

  // Group components by location type
  const groupedComponents = components.reduce((acc, comp) => {
    const type = comp.location.type || "NONE";
    if (!acc[type]) acc[type] = [];
    acc[type].push(comp);
    return acc;
  }, {});

  // Get unique box indices
  const boxIndices = [...new Set(
    (groupedComponents.BOX || []).map(c => c.location.index)
  )].sort((a, b) => a - b);

  // Get partition components sorted by index
  const partitionComponents = (groupedComponents.PARTITION || [])
    .sort((a, b) => a.location.index - b.location.index);

  // Assume 5x5 grid for partitions (adjust as needed)
  const gridSize = 5;
  const partitionGrid = Array(gridSize).fill().map(() => Array(gridSize).fill(null));
  partitionComponents.forEach(comp => {
    const row = Math.floor((comp.location.index - 1) / gridSize);
    const col = (comp.location.index - 1) % gridSize;
    if (row < gridSize && col < gridSize) {
      partitionGrid[row][col] = comp;
    }
  });

  const directComponents = groupedComponents.NONE || [];
  const boxComponents = selectedBox !== null
    ? (groupedComponents.BOX || []).filter(c => c.location.index === selectedBox)
    : [];

  if (loading) {
    return (
      <div className="text-center py-8">Loading components...</div>
    );
  }

  return (
    <div className="space-y-6">
        {/* Back button */}
        <button
          onClick={() => navigate("/containers")}
          className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded text-white"
        >
          ← Back to Containers
        </button>

        {/* Direct Components */}
        {directComponents.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold mb-3">Components in Container</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {directComponents.map(comp => (
                <ComponentCard key={comp.id} component={comp} />
              ))}
            </div>
          </div>
        )}

        {/* Boxes Dropdown */}
        {boxIndices.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold mb-3">Boxes</h3>
            <select
              value={selectedBox || ""}
              onChange={(e) => setSelectedBox(e.target.value ? parseInt(e.target.value) : null)}
              className="px-3 py-2 bg-zinc-800 border border-zinc-700 rounded text-white mb-4"
            >
              <option value="">Select a box...</option>
              {boxIndices.map(index => (
                <option key={index} value={index}>Box {index}</option>
              ))}
            </select>

            {selectedBox !== null && boxComponents.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {boxComponents.map(comp => (
                  <ComponentCard key={comp.id} component={comp} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Partitions Grid */}
        {partitionComponents.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold mb-3">Partitions</h3>
            <div className="grid gap-2" style={{ gridTemplateColumns: `repeat(${gridSize}, 1fr)` }}>
              {partitionGrid.map((row, rowIndex) =>
                row.map((comp, colIndex) => {
                  const partitionIndex = rowIndex * gridSize + colIndex + 1;
                  return (
                    <div
                      key={`${rowIndex}-${colIndex}`}
                      onClick={() => comp && setSelectedComponent(comp)}
                      className={`aspect-square border border-zinc-600 rounded flex flex-col items-center justify-center p-0 bg-zinc-800 relative overflow-hidden ${
                        comp ? 'cursor-pointer hover:border-blue-500 hover:shadow-lg transition-all' : ''
                      }`}
                    >
                      <div className="absolute top-0.5 left-0.5 text-white text-xs font-bold bg-zinc-700 bg-opacity-80 px-1 rounded z-10">
                        p{partitionIndex}
                      </div>
                      {comp ? (
                        <div className="w-full h-full">
                          <ComponentCard compact component={comp} />
                        </div>
                      ) : (
                        <span className="text-zinc-500 text-xs">Empty</span>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </div>
        )}

        {/* Component Detail Modal */}
        {selectedComponent && (
          <ComponentModal
            component={selectedComponent}
            onClose={() => setSelectedComponent(null)}
          />
        )}

        {directComponents.length === 0 && boxIndices.length === 0 && partitionComponents.length === 0 && (
          <div className="text-center text-zinc-400 py-8">
            No components found in this container.
          </div>
        )}
      </div>
  );
}

// Modal component for displaying larger component details
function ComponentModal({ component, onClose }) {
  if (!component) return null;

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-zinc-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-zinc-700"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 bg-zinc-800 border-b border-zinc-700 px-6 py-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-white">Component Details</h2>
          <button
            onClick={onClose}
            className="text-zinc-400 hover:text-white text-3xl font-bold leading-none"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Image */}
          <div className="flex justify-center mb-6">
            <img
              src={`${API_BASE}/${component.image_path}`}
              alt={component.name}
              className="max-w-full h-auto max-h-96 object-contain rounded-lg"
              onError={(e) => {
                e.currentTarget.src = "/placeholder.png";
              }}
            />
          </div>

          {/* Details */}
          <div className="space-y-4">
            <div>
              <label className="text-zinc-400 text-sm uppercase tracking-wide">Name</label>
              <p className="text-white text-2xl font-bold mt-1">{component.name}</p>
            </div>

            <div>
              <label className="text-zinc-400 text-sm uppercase tracking-wide">Category</label>
              <p className="text-white text-xl mt-1">{component.category}</p>
            </div>

            <div>
              <label className="text-zinc-400 text-sm uppercase tracking-wide">Quantity</label>
              <p className="text-white text-xl font-semibold mt-1">Qty: {component.quantity}</p>
            </div>

            {component.location && component.location.label && (
              <div>
                <label className="text-zinc-400 text-sm uppercase tracking-wide">Location</label>
                <p className="text-white text-xl mt-1">{component.location.label}</p>
              </div>
            )}

            {component.description && (
              <div>
                <label className="text-zinc-400 text-sm uppercase tracking-wide">Description</label>
                <p className="text-white text-lg mt-1">{component.description}</p>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-zinc-800 border-t border-zinc-700 px-6 py-4">
          <button
            onClick={onClose}
            className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white font-semibold"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

function ComponentCard({ component, compact = false }) {
  if (compact) {
    // Partition cell is square and can resize; use percentage sizing so
    // the image and text scale with the cell instead of fixed pixels.
    return (
      <div className="w-full h-full flex flex-col items-center justify-start p-0.5 box-border">
        {/* Image uses percentage of cell width so it scales with grid; increased to occupy more space */}
        <div className="w-full flex items-center justify-center" style={{ flex: '0 0 65%' }}>
          <img
            src={`${API_BASE}/${component.image_path}`}
            alt={component.name}
            style={{ width: '75%', height: '75%', objectFit: 'cover' }}
            className="rounded shrink-0"
            onError={(e) => {
              e.currentTarget.src = "/placeholder.png";
            }}
          />
        </div>

        {/* Text area: reduced space but larger fonts for readability */}
        <div className="w-full flex flex-col items-center justify-start px-1" style={{ flex: '0 0 35%' }}>
          <p className="text-white font-semibold text-[20px] leading-tight w-full text-center overflow-hidden" style={{ lineHeight: '1.05' }}>
            {component.name}
          </p>
          <p className="text-zinc-400 text-[15px] w-full text-center overflow-hidden truncate">
            {component.category}
          </p>
          <p className="text-zinc-300 text-[15px] font-semibold w-full text-center">
            Qty: {component.quantity}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-zinc-800 border border-zinc-700 rounded-lg p-4">
      <div className="flex items-center space-x-4">
        <img
          src={`${API_BASE}/${component.image_path}`}
          alt={component.name}
          className="w-16 h-16 object-cover rounded shrink-0"
          onError={(e) => {
            e.currentTarget.src = "/placeholder.png";
          }}
        />
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-white truncate text-lg">
            {component.name}
          </h4>
          <p className="text-zinc-400 text-base">
            {component.category}
          </p>
          <p className="text-zinc-300 text-base">
            Qty: {component.quantity}
          </p>
        </div>
      </div>
    </div>
  );
}
