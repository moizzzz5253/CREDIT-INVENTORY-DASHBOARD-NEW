import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import DashboardLayout from "../layouts/DashboardLayout";
import ComponentGrid from "../components/components/ComponentGrid";
import { getComponentsInContainer } from "../api/containers.api";

export default function ContainerDetail() {
  const { containerCode } = useParams();
  const [components, setComponents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getComponentsInContainer(containerCode)
      .then(setComponents)
      .finally(() => setLoading(false));
  }, [containerCode]);

  return (
    <DashboardLayout>
      <h2 className="text-xl font-semibold mb-4">
        Container {containerCode}
      </h2>

      {loading && <p className="text-zinc-400">Loading components...</p>}

      {!loading && components.length === 0 && (
        <p className="text-zinc-400">
          No components stored in this container.
        </p>
      )}

      {!loading && components.length > 0 && (
        <ComponentGrid components={components} />
      )}
    </DashboardLayout>
  );
}
