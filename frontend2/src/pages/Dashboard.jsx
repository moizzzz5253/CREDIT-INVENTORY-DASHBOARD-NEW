import {useEffect} from "react";
import DashboardLayout from "../layouts/DashboardLayout";
import Clock from "../components/dashboard/Clock";
import StatCard from "../components/dashboard/StatCard";

export default function Dashboard() {
  // Mock values for now
  const totalComponents = 1;
  const borrowedCount = 0;
  const overdueCount = 1;
    
  useEffect(() => {
    document.title = "Dashboard | CREDIT Inventory Management System";
  }, []);

  return (
    <DashboardLayout>
      <div className="grid-cols-1 gap-6">
        {/* Clock */}
        <div className="lg:col-span-1 flex items-center justify-center h-full">
          <Clock />
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatCard
            title="Total Components in Inventory"
            value={totalComponents}
          />
          <StatCard
            title="Currently Borrowed Components"
            value={borrowedCount}
          />
          <StatCard
            title="Overdue Borrows"
            value={overdueCount}
            variant="danger"
          />
        </div>
      </div>
    </DashboardLayout>
  );
}
