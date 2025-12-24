import {useEffect, useState} from "react";
import DashboardLayout from "../layouts/DashboardLayout";
import Clock from "../components/dashboard/Clock";
import StatCard from "../components/dashboard/StatCard";
import { getDashboardStats } from "../api/dashboard.api";

export default function Dashboard() {
  const [stats, setStats] = useState({
    total_components: 0,
    currently_borrowed: 0,
    overdue_borrows: 0
  });
  const [loading, setLoading] = useState(true);
    
  useEffect(() => {
    document.title = "Dashboard | CREDIT Inventory Management System";
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await getDashboardStats();
      setStats(data);
    } catch (error) {
      console.error("Failed to load dashboard stats:", error);
    } finally {
      setLoading(false);
    }
  };

  const overdueDisplay = stats.overdue_borrows === 0 
    ? { value: "No overdue", variant: "success" }
    : { value: stats.overdue_borrows, variant: "danger" };

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
            value={loading ? "..." : stats.total_components}
          />
          <StatCard
            title="Currently Borrowed Components"
            value={loading ? "..." : stats.currently_borrowed}
          />
          <StatCard
            title="Overdue Borrows"
            value={overdueDisplay.value}
            variant={overdueDisplay.variant}
          />
        </div>
      </div>
    </DashboardLayout>
  );
}
