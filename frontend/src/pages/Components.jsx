import DashboardLayout from "../layouts/DashboardLayout";
import AddComponentForm from "../components/components/AddComponentForm";

export default function Components() {
  
  return (
    <DashboardLayout>
      <AddComponentForm onSuccess={() => alert("Component added")} />
    </DashboardLayout>
  );
}
