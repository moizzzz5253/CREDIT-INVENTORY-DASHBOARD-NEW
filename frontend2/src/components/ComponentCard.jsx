import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import ComponentImage from "./ComponentImage";

export default function ComponentCard({ component, onModify, onDelete, onView }) {
  const [showActions, setShowActions] = useState(false);
  const navigate = useNavigate();

  const handleView = () => {
    if (onView) return onView(component);
    
    console.log("Component data for navigation:", component);
    
    const { 
      storage_type, 
      cabinet_number, 
      shelf_number, 
      container, 
      drawer_index, 
      storage_box_index, 
      location_type, 
      location_index 
    } = component;
    
    // Handle old data where storage_type might be null/undefined but has container
    // Extract cabinet_number from container code if not set (e.g., "A1" -> 1, "B2" -> 2)
    let effectiveCabinetNumber = cabinet_number;
    if (!effectiveCabinetNumber && container?.code) {
      try {
        const lastChar = container.code.slice(-1);
        const parsed = parseInt(lastChar);
        if (!isNaN(parsed)) {
          effectiveCabinetNumber = parsed;
        }
      } catch (e) {
        console.error("Failed to parse cabinet number from container code:", e);
      }
    }
    
    // Determine shelf number - prefer component's shelf_number, then container's, then default to 0
    const effectiveShelfNumber = shelf_number !== null && shelf_number !== undefined 
      ? shelf_number 
      : (container?.shelf_number !== null && container?.shelf_number !== undefined 
          ? container.shelf_number 
          : 0);
    
    // Priority: Check storage_type first, then fallback to container-based logic
    if (storage_type === 'DRAWER' && drawer_index) {
      let url = `/locations/drawer/${drawer_index}`;
      if (location_type === 'BOX' && location_index) {
        url += `?box=${location_index}`;
      } else if (location_type === 'PARTITION' && location_index) {
        url += `?partition=${location_index}`;
      }
      console.log("Navigating to drawer:", url);
      navigate(url);
      return;
    }
    
    if (storage_type === 'STORAGE_BOX' && storage_box_index) {
      const url = `/locations/storage-box/${storage_box_index}`;
      console.log("Navigating to storage box:", url);
      navigate(url);
      return;
    }
    
    // Cabinet storage or old data with container (assumed to be in cabinet)
    if (storage_type === 'CABINET' || (!storage_type && (effectiveCabinetNumber || container?.code))) {
      if (container?.code) {
        // Has container - navigate with box/partition params
        const finalCabinetNum = effectiveCabinetNumber || (container.code ? parseInt(container.code.slice(-1)) : null);
        
        if (finalCabinetNum) {
          let url = `/locations/cabinet/${finalCabinetNum}/shelf/${effectiveShelfNumber}/container/${container.code}`;
          if (location_type === 'BOX' && location_index) {
            url += `?box=${location_index}`;
          } else if (location_type === 'PARTITION' && location_index) {
            url += `?partition=${location_index}`;
          }
          console.log("Navigating to cabinet container:", url);
          navigate(url);
          return;
        }
      } else if (effectiveCabinetNumber) {
        // Bare on shelf (no container)
        const url = `/locations/cabinet/${effectiveCabinetNumber}/shelf/${effectiveShelfNumber}`;
        console.log("Navigating to cabinet shelf:", url);
        navigate(url);
        return;
      }
    }
    
    // Fallback: Try old container navigation
    if (container?.code) {
      let url = `/containers/${container.code}`;
      if (location_type === 'BOX' && location_index) {
        url += `?box=${location_index}`;
      } else if (location_type === 'PARTITION' && location_index) {
        url += `?partition=${location_index}`;
      }
      console.log("Navigating to container (fallback):", url);
      navigate(url);
      return;
    }
    
    // Last resort: show alert
    console.warn("Could not determine navigation path for component:", component);
    alert(`Location: ${getLocationLabel(component)}\n\nNavigation not available for this component.`);
  };

  // Get location label from API response
  const getLocationLabel = (component) => {
    // Use the location label from the API (already formatted correctly)
    if (component?.location?.label) {
      return component.location.label; // e.g. "Cabinet 1 Shelf 2 A2-b1", "Drawer 1", "Storage Box 1"
    }
    // Fallback for old data
    return component?.container?.code ?? "Unknown Location";
  };

  return (
    <div
      className="bg-zinc-800 border border-zinc-700 rounded-lg p-4 cursor-pointer hover:shadow-lg"
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
      onClick={() => setShowActions((s) => !s)}
    >
      <div className="flex items-center space-x-2 sm:space-x-4">
        <ComponentImage
          imagePath={component.image_path}
          alt={component.name}
          className="w-16 h-16 sm:w-24 sm:h-24 object-cover rounded flex-shrink-0"
        />

        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-white truncate text-base sm:text-xl">
            {component.name}
          </h4>

          <p className="text-zinc-400 text-sm sm:text-base">{component.category}</p>
          {component.is_controlled && (
            <div className="mb-1 sm:mb-2 px-2 sm:px-3 py-0.5 sm:py-1 bg-orange-600 text-white text-[10px] sm:text-xs font-bold rounded inline-block">
              CONTROLLED
            </div>
          )}
          <p className="text-zinc-300 text-sm sm:text-base">Qty: {component.quantity}</p>
          <p className="text-zinc-300 text-sm sm:text-base">
            Borrowed: {component.borrowed_quantity}
          </p>

          <p className="text-zinc-400 text-xs sm:text-sm truncate">
            Location: {getLocationLabel(component)}
          </p>

          {component.remarks && (
            <p className="text-zinc-400 text-[10px] sm:text-xs mt-1 line-clamp-2">
              Remarks: {component.remarks}
            </p>
          )}
        </div>
      </div>

      {showActions && (
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onModify && onModify(component);
            }}
            className="px-2 sm:px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-white text-xs sm:text-sm flex-1 sm:flex-none"
          >
            Modify
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete && onDelete(component);
            }}
            className="px-2 sm:px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-white text-xs sm:text-sm flex-1 sm:flex-none"
          >
            Delete
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation();
              handleView();
            }}
            className="px-2 sm:px-3 py-1 bg-emerald-600 hover:bg-emerald-700 rounded text-white text-xs sm:text-sm flex-1 sm:flex-none"
          >
            View Location
          </button>
        </div>
      )}
    </div>
  );
}
