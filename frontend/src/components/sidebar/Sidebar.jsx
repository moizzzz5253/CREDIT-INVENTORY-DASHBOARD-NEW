import { useNavigate, useLocation } from "react-router-dom";
import SidebarItem from "./SidebarItem";

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <aside className="w-64 border-r border-zinc-800 p-4">
      <h1 className="text-lg font-semibold mb-6">
        Inventory Dashboard
      </h1>

      <nav className="space-y-2">
        <SidebarItem
          label="Containers"
          active={location.pathname === "/containers"}
          onClick={() => navigate("/containers")}
        />
        <SidebarItem
          label="Components"
          active={location.pathname === "/components"}
          onClick={() => navigate("/components")}
        />
       <SidebarItem
          label="Borrow"
          active={location.pathname === "/borrow"}
          onClick={() => navigate("/borrow")}
        />

        <SidebarItem label="Return" />
        <SidebarItem label="History" />
      </nav>
    </aside>
  );
}
