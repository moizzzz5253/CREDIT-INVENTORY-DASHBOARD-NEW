import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  getCabinetsWithComponents,
  getDrawersWithComponents,
  getStorageBoxesWithComponents,
} from "../api/locations.api";

export default function Locations() {
  const navigate = useNavigate();
  const [cabinetCount, setCabinetCount] = useState(0);
  const [drawerCount, setDrawerCount] = useState(0);
  const [storageBoxCount, setStorageBoxCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCounts();
  }, []);

  const loadCounts = async () => {
    try {
      const [cabinets, drawers, storageBoxes] = await Promise.all([
        getCabinetsWithComponents(),
        getDrawersWithComponents(),
        getStorageBoxesWithComponents(),
      ]);
      console.log("Location counts loaded:", { cabinets, drawers, storageBoxes });
      setCabinetCount(Array.isArray(cabinets) ? cabinets.length : 0);
      setDrawerCount(Array.isArray(drawers) ? drawers.length : 0);
      setStorageBoxCount(Array.isArray(storageBoxes) ? storageBoxes.length : 0);
    } catch (error) {
      console.error("Failed to load location counts:", error);
      console.error("Error details:", error.response?.data || error.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-8 text-zinc-400">Loading locations...</div>
    );
  }

  return (
    <div className="space-y-4 sm:space-y-6 px-2 sm:px-0">
      <h1 className="text-2xl sm:text-3xl font-bold text-white mb-4 sm:mb-6">Locations</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 sm:gap-6">
        {/* Cabinet Card */}
        <div
          onClick={() => navigate("/locations/cabinet")}
          className="bg-zinc-800 border border-zinc-700 rounded-lg p-4 sm:p-6 cursor-pointer hover:border-blue-500 hover:shadow-lg transition-all"
        >
          <div className="flex items-center justify-between mb-3 sm:mb-4">
            <h2 className="text-xl sm:text-2xl font-bold text-white">Cabinets</h2>
            <div className="text-3xl sm:text-4xl">🗄️</div>
          </div>
          <p className="text-zinc-400 mb-2 text-sm sm:text-base">
            {cabinetCount} cabinet{cabinetCount !== 1 ? "s" : ""} with components
          </p>
          <p className="text-zinc-500 text-xs sm:text-sm">
            View components organized by cabinet and shelf
          </p>
        </div>

        {/* Drawer Card */}
        <div
          onClick={() => navigate("/locations/drawer")}
          className="bg-zinc-800 border border-zinc-700 rounded-lg p-4 sm:p-6 cursor-pointer hover:border-blue-500 hover:shadow-lg transition-all"
        >
          <div className="flex items-center justify-between mb-3 sm:mb-4">
            <h2 className="text-xl sm:text-2xl font-bold text-white">Drawers</h2>
            <div className="text-3xl sm:text-4xl">🗄️</div>
          </div>
          <p className="text-zinc-400 mb-2 text-sm sm:text-base">
            {drawerCount} drawer{drawerCount !== 1 ? "s" : ""} with components
          </p>
          <p className="text-zinc-500 text-xs sm:text-sm">
            View components stored in drawers
          </p>
        </div>

        {/* Storage Box Card */}
        <div
          onClick={() => navigate("/locations/storage-box")}
          className="bg-zinc-800 border border-zinc-700 rounded-lg p-4 sm:p-6 cursor-pointer hover:border-blue-500 hover:shadow-lg transition-all"
        >
          <div className="flex items-center justify-between mb-3 sm:mb-4">
            <h2 className="text-xl sm:text-2xl font-bold text-white">Storage Boxes</h2>
            <div className="text-3xl sm:text-4xl">📦</div>
          </div>
          <p className="text-zinc-400 mb-2 text-sm sm:text-base">
            {storageBoxCount} storage box{storageBoxCount !== 1 ? "es" : ""} with components
          </p>
          <p className="text-zinc-500 text-xs sm:text-sm">
            View components stored in storage boxes
          </p>
        </div>
      </div>
    </div>
  );
}

