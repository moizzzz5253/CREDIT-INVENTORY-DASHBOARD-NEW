import Sidebar from "../components/sidebar/Sidebar";

export default function DashboardLayout({ children }) {
  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-100">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-6">
        {children}
      </main>
    </div>
  );
}
