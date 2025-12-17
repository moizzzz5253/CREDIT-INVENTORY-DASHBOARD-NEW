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

  return (
    <DashboardLayout>
      <ContainerHeader
        onInit={handleInit}
        onRegenerate={handleRegenerate}
        hasContainers={containers.length > 0}
      />
      <ContainerGrid containers={containers} />
    </DashboardLayout>
  );
}
