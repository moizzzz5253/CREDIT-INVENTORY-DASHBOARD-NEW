export default function ComponentCard({ component }) {
  return (
    <div className="bg-zinc-800 border border-zinc-700 rounded-lg p-4">
      <img
        src={`${import.meta.env.VITE_API_BASE_URL}${component.image_path}`}
        alt={component.name}
        className="h-32 w-full object-contain bg-white rounded mb-3"
      />

      <h4 className="font-semibold">{component.name}</h4>
      <p className="text-sm text-zinc-450">{component.category}</p>

      <div className="mt-2 text-sm">
        Quantity: <span className="font-medium">{component.quantity}</span>
      </div>

      {component.remarks && (
        <p className="text-xs text-zinc-400 mt-2">
          {component.remarks}
        </p>
      )}
    </div>
  );
}
