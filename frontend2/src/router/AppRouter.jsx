import React, { useEffect } from "react";
import { Routes, Route, Navigate, BrowserRouter } from "react-router-dom";
import Dashboard from "../pages/Dashboard";
import Containers from "../pages/Containers";
import ContainerDetail from "../pages/ContainerDetail";
import ManageComponents from "../pages/ManageComponents";
import AddComponent from "../pages/AddComponent";
import BorrowNew from "../pages/BorrowNew";
import BorrowActive from "../pages/BorrowActive";
import History from "../pages/History";
import SystemManager from "../pages/SystemManager";
import AccountSettings from "../pages/AccountSettings";
import DashboardLayout from "../layouts/DashboardLayout";
import ProtectedRoute from "../components/ProtectedRoute";
import Locations from "../pages/Locations";
import CabinetList from "../pages/locations/CabinetList";
import CabinetDetail from "../pages/locations/CabinetDetail";
import ShelfView from "../pages/locations/ShelfView";
import DrawerList from "../pages/locations/DrawerList";
import DrawerDetail from "../pages/locations/DrawerDetail";
import StorageBoxList from "../pages/locations/StorageBoxList";
import StorageBoxDetail from "../pages/locations/StorageBoxDetail";

export default function AppRouter() {
  // #region agent log
  useEffect(() => {
    fetch('http://127.0.0.1:7242/ingest/d55c5050-20f8-400e-ab29-1c5521b877bb',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AppRouter.jsx:13',message:'AppRouter component mounted',data:{path:window.location.pathname,hasRoutes:true},timestamp:Date.now(),sessionId:'debug-session',runId:'run2',hypothesisId:'C'})}).catch(()=>{});
  }, []);
  // #endregion
  // #region agent log
  try {
    fetch('http://127.0.0.1:7242/ingest/d55c5050-20f8-400e-ab29-1c5521b877bb',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'AppRouter.jsx:17',message:'AppRouter returning JSX',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run2',hypothesisId:'C'})}).catch(()=>{});
  } catch(e) {}
  // #endregion
  return (
   <BrowserRouter>
    <DashboardLayout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/containers" element={<Containers />} />
        <Route path="/containers/:code" element={<ContainerDetail />} />
        <Route path="/components" element={<ManageComponents />} />
        <Route path="/components/add" element={<AddComponent />} />
        <Route path="/borrow/new" element={<BorrowNew />} />
        <Route path="/borrow/active" element={<BorrowActive />} />
        <Route path="/history" element={<History />} />
        <Route
          path="/system-manager"
          element={
            <ProtectedRoute>
              <SystemManager />
            </ProtectedRoute>
          }
        />
        <Route path="/account-settings" element={<AccountSettings />} />
        <Route path="/locations" element={<Locations />} />
        <Route path="/locations/cabinet" element={<CabinetList />} />
        <Route path="/locations/cabinet/:cabinetNumber" element={<CabinetDetail />} />
        <Route path="/locations/cabinet/:cabinetNumber/shelf/:shelfNumber" element={<ShelfView />} />
        <Route path="/locations/cabinet/:cabinetNumber/shelf/:shelfNumber/container/:code" element={<ContainerDetail />} />
        <Route path="/locations/drawer" element={<DrawerList />} />
        <Route path="/locations/drawer/:drawerIndex" element={<DrawerDetail />} />
        <Route path="/locations/storage-box" element={<StorageBoxList />} />
        <Route path="/locations/storage-box/:boxIndex" element={<StorageBoxDetail />} />
      </Routes>
    </DashboardLayout>
   </BrowserRouter>
  );
}
