import React from "react";
import ComponentCard from "../ComponentCard";

/**
 * StorageBoxVisualization - Visual representation of a storage box
 * Shows components arranged in a grid layout
 */
export default function StorageBoxVisualization({ components }) {
  if (!components || components.length === 0) {
    return (
      <div className="bg-zinc-800 border border-zinc-700 rounded-lg p-8 text-center">
        <div className="text-zinc-400">Storage box is empty</div>
      </div>
    );
  }

  return (
    <div className="bg-zinc-800 border border-zinc-700 rounded-lg p-6">
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
        {components.map((component) => (
          <ComponentCard key={component.id} component={component} />
        ))}
      </div>
    </div>
  );
}

