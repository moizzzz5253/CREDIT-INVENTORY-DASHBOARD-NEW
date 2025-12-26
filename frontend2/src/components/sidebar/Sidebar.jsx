import React from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Box,
  Cpu,
  ArrowLeftRight,
  History,
  Settings
} from "lucide-react";

const menu = [
  { name: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
  { name: "Containers", path: "/containers", icon: Box },
  { name: "Components", path: "/components", icon: Cpu },
  { name: "Borrow & Return", path: "/borrow/active", icon: ArrowLeftRight },
  { name: "History", path: "/history", icon: History },
  { name: "System Manager", path: "/system-manager", icon: Settings },
];

export default function Sidebar({ isOpen, onClose }) {
  // #region agent log
  try {
    fetch('http://127.0.0.1:7242/ingest/d55c5050-20f8-400e-ab29-1c5521b877bb',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Sidebar.jsx:20',message:'Sidebar rendering',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run2',hypothesisId:'C'})}).catch(()=>{});
  } catch(e) {}
  // #endregion
  
  const handleNavClick = () => {
    // Close sidebar on mobile when a link is clicked
    if (window.innerWidth < 768 && onClose) {
      onClose();
    }
  };

  return (
    <aside
      className={`
        fixed md:static
        top-0 left-0
        h-full w-64
        bg-zinc-900 text-zinc-200
        flex flex-col
        border-r border-zinc-800
        z-50
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}
    >
      {/* Logo / Title */}
      <div className="px-6 py-5 text-xl font-bold border-b border-zinc-800">
        CREDIT IMS
      </div>

      {/* Menu */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {menu.map(({ name, path, icon: Icon }) => (
          <NavLink
            key={name}
            to={path}
            onClick={handleNavClick}
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
