import { Routes, Route, Navigate, BrowserRouter } from "react-router-dom";
import Dashboard from "../pages/Dashboard";
import Containers from "../pages/Containers";
import ContainerDetail from "../pages/ContainerDetail";
import ManageComponents from "../pages/ManageComponents";
import AddComponent from "../pages/AddComponent";
import BorrowNew from "../pages/BorrowNew";
import BorrowActive from "../pages/BorrowActive";
import DashboardLayout from "../layouts/DashboardLayout";

export default function AppRouter() {
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
      </Routes>
    </DashboardLayout>
   </BrowserRouter>
  );
}
