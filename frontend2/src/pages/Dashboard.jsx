import React, {useEffect, useState} from "react";
import { useNavigate } from "react-router-dom";
import Clock from "../components/dashboard/Clock";
import StatCard from "../components/dashboard/StatCard";
import PasswordPromptModal from "../components/PasswordPromptModal";
import { getDashboardStats } from "../api/dashboard.api";
import { verifyAdminPassword } from "../api/admin.api";
import { User } from "lucide-react";

export default function Dashboard() {
  const [stats, setStats] = useState({
    total_components: 0,
    currently_borrowed: 0,
    overdue_borrows: 0
  });
  const [loading, setLoading] = useState(true);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [passwordError, setPasswordError] = useState("");
  const navigate = useNavigate();
    
  useEffect(() => {
    document.title = "Dashboard | CREDIT Inventory Management System";
    loadStats();
  }, []);

  const loadStats = async () => {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/d55c5050-20f8-400e-ab29-1c5521b877bb',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Dashboard.jsx:20',message:'loadStats called',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    try {
      const data = await getDashboardStats();
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/d55c5050-20f8-400e-ab29-1c5521b877bb',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Dashboard.jsx:23',message:'getDashboardStats success',data:{hasData:!!data,dataKeys:data?Object.keys(data):[]},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
      // #endregion
      setStats(data);
    } catch (error) {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/d55c5050-20f8-400e-ab29-1c5521b877bb',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Dashboard.jsx:25',message:'getDashboardStats error',data:{error:error.message,stack:error.stack},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
      // #endregion
      console.error("Failed to load dashboard stats:", error);
    } finally {
      setLoading(false);
    }
  };

  const overdueDisplay = stats.overdue_borrows === 0 
    ? { value: "No overdue", variant: "success" }
    : { value: stats.overdue_borrows, variant: "danger" };

  const handleAdminClick = () => {
    setPasswordError("");
    setShowPasswordModal(true);
  };

  const handlePasswordVerify = async (password) => {
    try {
      const result = await verifyAdminPassword(password);
      if (result.success) {
        setShowPasswordModal(false);
        setPasswordError("");
        // Navigate to account settings
        navigate("/account-settings");
      } else {
        setPasswordError(result.message || "Invalid password");
      }
    } catch (error) {
      setPasswordError(error.response?.data?.detail || "Failed to verify password");
    }
  };

  const handleCloseModal = () => {
    setShowPasswordModal(false);
    setPasswordError("");
  };

  // #region agent log
  useEffect(() => {
    fetch('http://127.0.0.1:7242/ingest/d55c5050-20f8-400e-ab29-1c5521b877bb',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Dashboard.jsx:43',message:'Dashboard component mounted',data:{loading,stats:Object.keys(stats)},timestamp:Date.now(),sessionId:'debug-session',runId:'run2',hypothesisId:'C'})}).catch(()=>{});
  }, []);
  // #endregion
  // #region agent log
  try {
    fetch('http://127.0.0.1:7242/ingest/d55c5050-20f8-400e-ab29-1c5521b877bb',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Dashboard.jsx:47',message:'Dashboard returning JSX',data:{loading},timestamp:Date.now(),sessionId:'debug-session',runId:'run2',hypothesisId:'C'})}).catch(()=>{});
  } catch(e) {}
  // #endregion
  return (
    <div className="space-y-6">
      {/* Admin Button - Top Right */}
      <button
        onClick={handleAdminClick}
        className="fixed top-4 right-4 z-50 bg-zinc-800 hover:bg-zinc-700 p-2 rounded-md text-white transition-colors flex items-center space-x-2"
        aria-label="Admin Settings"
      >
        <User size={20} />
        <span className="hidden md:inline">Admin</span>
      </button>

      {/* Password Prompt Modal */}
      <PasswordPromptModal
        isOpen={showPasswordModal}
        onClose={handleCloseModal}
        onVerify={handlePasswordVerify}
        error={passwordError}
      />
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
  );
}
