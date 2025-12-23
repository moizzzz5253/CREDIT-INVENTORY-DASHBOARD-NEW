import { Routes, Route, Navigate, BrowserRouter } from "react-router-dom";
import Dashboard from "../pages/Dashboard";
import Containers from "../pages/Containers";

export default function AppRouter() {
  return (
   <BrowserRouter>
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/containers" element={<Containers />} />
    </Routes>
   </BrowserRouter>
  );
}
