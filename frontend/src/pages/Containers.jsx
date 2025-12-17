import { useEffect, useState } from "react";
import DashboardLayout from "../layouts/DashboardLayout";
import ContainerHeader from "../components/containers/ContainerHeader";
import ContainerGrid from "../components/containers/ContainerGrid";

import {
  getAllContainers,
  initContainers,
  regenerateQRCodes,
} from "../api/containers.api";

export default function Containers() {
  const [containers, setContainers] = useState([]);
  const [search, setSearch] = useState("");


  const fetchContainers = async () => {
    const data = await getAllContainers();
    setContainers(Array.isArray(data) ? data : []);
  };

  useEffect(() => {
    fetchContainers();
  }, []);

  const handleInit = async () => {
    await initContainers();
    fetchContainers();
  };

  const handleRegenerate = async () => {
    await regenerateQRCodes();
    fetchContainers();
  };
  const filteredContainers = containers.filter((c) => {
    const query = search.toLowerCase();
    return (
      c.code.toLowerCase().includes(query) ||
      String(c.cabinet_number).includes(query)
    );
  });


  return (
    <DashboardLayout>
      <ContainerHeader
        onInit={handleInit}
        onRegenerate={handleRegenerate}
        hasContainers={containers.length > 0}
      />
      <input
        type="text"
        placeholder="Search by container code or cabinet number..."
        className="bg-zinc-800 border border-zinc-700 rounded-md px-4 py-2 mb-4 w-full
                  focus:outline-none focus:ring-2 focus:ring-blue-500"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

     <ContainerGrid containers={filteredContainers} />


    </DashboardLayout>
  );
}
