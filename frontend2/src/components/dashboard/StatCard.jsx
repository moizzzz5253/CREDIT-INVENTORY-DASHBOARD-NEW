export default function StatCard({ title, value, variant = "default" }) {
  const variants = {
    default: "bg-zinc-800 border-zinc-700",
    danger: "bg-red-900 border-red-700 text-red-200",
  };

  return (
    <div
      className={`p-5 rounded-lg border ${variants[variant]} flex flex-col gap-2`}
    >
      <span className="text-sm text-zinc-400">{title}</span>
      <span className="text-3xl font-bold">{value}</span>
    </div>
  );
}
