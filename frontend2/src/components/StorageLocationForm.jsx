import React from "react";

/**
 * StorageLocationForm - Reusable component for storage location selection
 * Used in both AddComponent and ManageComponents
 */
export default function StorageLocationForm({
  storageType,
  cabinetNumber,
  shelfNumber,
  containerId,
  drawerIndex,
  storageBoxIndex,
  locationType,
  locationIndex,
  containers = [],
  onStorageTypeChange,
  onCabinetNumberChange,
  onShelfNumberChange,
  onContainerIdChange,
  onDrawerIndexChange,
  onStorageBoxIndexChange,
  onLocationTypeChange,
  onLocationIndexChange,
}) {
  // Filter containers by selected cabinet
  const filteredContainers = storageType === "CABINET" && cabinetNumber
    ? containers.filter(c => c.cabinet_number === cabinetNumber)
    : [];

  return (
    <div className="space-y-4">
      {/* Storage Type Selection */}
      <div>
        <label className="block text-sm font-medium text-zinc-300">Store In</label>
        <select
          value={storageType || "CABINET"}
          onChange={(e) => onStorageTypeChange(e.target.value)}
          className="mt-1 block w-full rounded bg-zinc-900 border border-zinc-700 p-2 text-white"
        >
          <option value="CABINET">Cabinet</option>
          <option value="DRAWER">Drawer</option>
          <option value="STORAGE_BOX">Storage Box</option>
        </select>
      </div>

      {/* Cabinet Storage Fields */}
      {storageType === "CABINET" && (
        <>
          <div>
            <label className="block text-sm font-medium text-zinc-300">Cabinet Number</label>
            <select
              value={cabinetNumber || ""}
              onChange={(e) => onCabinetNumberChange(parseInt(e.target.value, 10))}
              className="mt-1 block w-full rounded bg-zinc-900 border border-zinc-700 p-2 text-white"
              required
            >
              <option value="">Select Cabinet</option>
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(num => (
                <option key={num} value={num}>Cabinet {num}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-300">Shelf Number</label>
            <select
              value={shelfNumber !== undefined ? shelfNumber : ""}
              onChange={(e) => onShelfNumberChange(parseInt(e.target.value, 10))}
              className="mt-1 block w-full rounded bg-zinc-900 border border-zinc-700 p-2 text-white"
              required
            >
              <option value="">Select Shelf</option>
              <option value="0">No Shelf (0)</option>
              {[1, 2, 3, 4, 5].map(num => (
                <option key={num} value={num}>Shelf {num}</option>
              ))}
            </select>
          </div>

          {/* Container Selection (only if shelf > 0) */}
          {shelfNumber !== undefined && shelfNumber > 0 && (
            <div>
              <label className="block text-sm font-medium text-zinc-300">Container (Optional)</label>
              <select
                value={containerId || ""}
                onChange={(e) => onContainerIdChange(e.target.value ? parseInt(e.target.value, 10) : null)}
                className="mt-1 block w-full rounded bg-zinc-900 border border-zinc-700 p-2 text-white"
              >
                <option value="">No Container (Bare on Shelf)</option>
                {filteredContainers.map(c => (
                  <option key={c.id} value={c.id}>{c.code}</option>
                ))}
              </select>
              {filteredContainers.length === 0 && cabinetNumber && (
                <p className="text-zinc-500 text-sm mt-1">No containers found for Cabinet {cabinetNumber}</p>
              )}
            </div>
          )}
        </>
      )}

      {/* Drawer Storage Fields */}
      {storageType === "DRAWER" && (
        <div>
          <label className="block text-sm font-medium text-zinc-300">Drawer Index</label>
          <input
            type="number"
            min="1"
            value={drawerIndex || ""}
            onChange={(e) => onDrawerIndexChange(parseInt(e.target.value, 10))}
            className="mt-1 block w-full rounded bg-zinc-900 border border-zinc-700 p-2 text-white"
            placeholder="Enter drawer number (1, 2, 3...)"
            required
          />
        </div>
      )}

      {/* Storage Box Fields */}
      {storageType === "STORAGE_BOX" && (
        <div>
          <label className="block text-sm font-medium text-zinc-300">Storage Box Index</label>
          <input
            type="number"
            min="1"
            value={storageBoxIndex || ""}
            onChange={(e) => onStorageBoxIndexChange(parseInt(e.target.value, 10))}
            className="mt-1 block w-full rounded bg-zinc-900 border border-zinc-700 p-2 text-white"
            placeholder="Enter storage box number (1, 2, 3...)"
            required
          />
        </div>
      )}

      {/* Box/Partition Selection (for Cabinet with container or Drawer) */}
      {(storageType === "CABINET" && containerId) || storageType === "DRAWER" ? (
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-zinc-300">Box/Partition (Optional)</label>
            <select
              value={locationType || "NONE"}
              onChange={(e) => onLocationTypeChange(e.target.value)}
              className="mt-1 block w-full rounded bg-zinc-900 border border-zinc-700 p-2 text-white"
            >
              <option value="NONE">None</option>
              <option value="BOX">Box</option>
              <option value="PARTITION">Partition</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-zinc-300">Index (1-15)</label>
            <input
              type="number"
              min="1"
              max="15"
              value={locationIndex || ""}
              onChange={(e) => onLocationIndexChange(e.target.value ? parseInt(e.target.value, 10) : null)}
              disabled={locationType === "NONE"}
              className="mt-1 block w-full rounded bg-zinc-900 border border-zinc-700 p-2 text-white disabled:opacity-50"
              placeholder="1-15"
            />
          </div>
        </div>
      ) : null}
    </div>
  );
}

