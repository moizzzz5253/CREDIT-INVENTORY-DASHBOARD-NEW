import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Containers from "../pages/Containers";
import Components from "../pages/Components";
import ContainerDetail from "../pages/ContainerDetail";
import ContainerPrint from "../pages/ContainerPrint";
import Borrow from "../pages/Borrow";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/containers" />} />

        <Route path="/containers" element={<Containers />} />
        <Route path="/containers/print" element={<ContainerPrint />} />
        <Route path="/containers/:containerCode" element={<ContainerDetail />} />

        <Route path="/components" element={<Components />} />
        <Route path="/borrow" element={<Borrow />} />
      </Routes>
    </BrowserRouter>
  );
}
