export default function StatCard({ title, value, variant = "default" }) {
  const variants = {
    default: "bg-zinc-800 border-zinc-700",
    danger: "bg-red-900 border-red-700 text-red-200",
    success: "bg-green-900 border-green-700 text-green-200",
  };

  return (
    <div
      className={`p-6 rounded-lg border ${variants[variant]} flex flex-col gap-2`}
    >
      <span className="text-lg text-zinc-400">{title}</span>
      <span className="text-5xl font-bold">{value}</span>
    </div>
  );
}
