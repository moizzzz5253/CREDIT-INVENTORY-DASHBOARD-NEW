import { useEffect, useState } from "react";
import DashboardLayout from "../layouts/DashboardLayout";
import AddComponentForm from "../components/components/AddComponentForm";
import { getAllComponents } from "../api/components.api";

export default function Components() {
  const [view, setView] = useState("manage"); // add | manage

  const [components, setComponents] = useState([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("ALL");
  const [selectedComponent, setSelectedComponent] = useState(null);

  useEffect(() => {
    fetchComponents();
  }, []);

  const fetchComponents = async () => {
    const data = await getAllComponents();
    setComponents(data);
  };

  const filteredComponents = components.filter((c) => {
    const matchesSearch = c.name
      .toLowerCase()
      .includes(search.toLowerCase());

    const matchesCategory = category === "ALL" || c.category === category;

    return matchesSearch && matchesCategory;
  });

  return (
    <DashboardLayout>
      {/* Top toggle */}
      <div className="flex gap-4 mb-6">
        <button
          className={`px-4 py-2 rounded ${
            view === "add" ? "bg-blue-600" : "bg-zinc-700"
          }`}
          onClick={() => setView("add")}
        >
          Add Component
        </button>
        <button
          className={`px-4 py-2 rounded ${
            view === "manage" ? "bg-blue-600" : "bg-zinc-700"
          }`}
          onClick={() => setView("manage")}
        >
          Manage Components
        </button>
      </div>

      {/* MANAGE COMPONENTS */}
      {view === "manage" && (
        <div>
          {/* Search */}
          <input
            type="text"
            placeholder="Search component name..."
            className="w-full p-2 mb-3 bg-zinc-800 rounded"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />

          {/* Category filter */}
          <select
            className="w-full p-2 mb-4 bg-zinc-800 rounded"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="ALL">All Categories</option>
            <option value="Microcontrollers">Microcontrollers</option>
            <option value="Mini Computers">Mini Computers</option>
            <option value="Drone Components">Drone Components</option>
            <option value="Batteries and Accessories">Batteries and Accessories</option>
            <option value="Cables (USB, Display, Data)">Cables (USB, Display, Data)</option>
            <option value="Chargers and Power Cables">Chargers and Power Cables</option>
            <option value="Jumper Wires">Jumper Wires</option>
            <option value="Electrical Appliances">Electrical Appliances</option>
            <option value="DIY Tools">DIY Tools</option>
            <option value="Hardware Accessories">Hardware Accessories</option>
            <option value="Network Devices and Cables">Network Devices and Cables</option>
            <option value="Robotics Components">Robotics Components</option>
            <option value="Motors and Motor Drivers">Motors and Motor Drivers</option>
            <option value="Electronic Components">Electronic Components</option>
            <option value="Measuring Instruments">Measuring Instruments</option>
            <option value="Stationery">Stationery</option>
            <option value="3D Printing Tools">3D Printing Tools</option>
          </select>

          {/* Component list */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {filteredComponents.map((c) => (
              <div
                key={c.id}
                className={`p-3 rounded border cursor-pointer ${
                  selectedComponent?.id === c.id
                    ? "border-blue-500 bg-zinc-800"
                    : "border-zinc-700 bg-zinc-900"
                }`}
                onClick={() => setSelectedComponent(c)}
              >
                <div className="font-semibold">{c.name}</div>
                <div className="text-sm text-zinc-400">{c.category}</div>
                <div className="text-sm">Qty: {c.quantity}</div>
              </div>
            ))}
          </div>

          {/* Actions */}
          {selectedComponent && (
            <div className="flex gap-3 mt-4">
              <button className="px-4 py-2 bg-blue-600 rounded">
                Modify Component
              </button>
              <button className="px-4 py-2 bg-red-600 rounded">
                Delete Component
              </button>
            </div>
          )}
        </div>
      )}

      {/* ADD COMPONENT */}
         {view === "add" && (
        <AddComponentForm
          onSuccess={() => {
            fetchComponents();
            setView("manage");
          }}
        />
      )}
    </DashboardLayout>
  );
}

