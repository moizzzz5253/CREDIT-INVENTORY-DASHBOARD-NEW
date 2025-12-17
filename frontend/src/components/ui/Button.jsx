export default function Button({ children, onClick, variant = "primary" }) {
  const base =
    "px-4 py-2 rounded-md font-medium transition focus:outline-none";

  const variants = {
    primary: "bg-blue-600 hover:bg-blue-500 text-white",
    secondary: "bg-zinc-700 hover:bg-zinc-600 text-white",
  };

  return (
    <button onClick={onClick} className={`${base} ${variants[variant]}`}>
      {children}
    </button>
  );
}
