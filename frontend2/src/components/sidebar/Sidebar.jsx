import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Box,
  Cpu,
  Handshake,
  RotateCcw,
  History
} from "lucide-react";

const menu = [
  { name: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
  { name: "Containers", path: "/containers", icon: Box },
  { name: "Components", path: "/components", icon: Cpu },
  { name: "Borrow", path: "/borrow", icon: Handshake },
  { name: "Return", path: "/returns", icon: RotateCcw },
  { name: "History", path: "/history", icon: History },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-zinc-900 text-zinc-200 flex flex-col border-r border-zinc-800">
      {/* Logo / Title */}
      <div className="px-6 py-5 text-xl font-bold border-b border-zinc-800">
        CREDIT IMS
      </div>

      {/* Menu */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {menu.map(({ name, path, icon: Icon }) => (
          <NavLink
            key={name}
            to={path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2 rounded-md transition
               ${
                 isActive
                   ? "bg-zinc-800 text-white"
                   : "text-zinc-400 hover:bg-zinc-800 hover:text-white"
               }`
            }
          >
            <Icon size={20} />
            <span className="text-sm font-medium">{name}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
