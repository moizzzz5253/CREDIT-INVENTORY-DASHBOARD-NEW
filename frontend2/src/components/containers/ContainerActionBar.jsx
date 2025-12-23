export default function ContainerActionBar({
  search,
  onSearchChange,
  onInit,
  onPrint,
  onRegenerate,
  disableInit,
}) {
  return (
    <div className="flex flex-col sm:flex-row gap-4 justify-between mb-6">
      {/* Search */}
      <input
        type="text"
        placeholder="Search container (A1, B2...)"
        value={search}
        onChange={(e) => onSearchChange(e.target.value)}
        className="
          bg-zinc-800
          border
          border-zinc-700
          rounded
          px-4
          py-2
          text-white
          w-full
          sm:w-64
        "
      />

      {/* Actions */}
      <div className="flex gap-3">
        <button
          onClick={onInit}
          disabled={disableInit}
          className="
            px-4 py-2 rounded
            bg-green-600
            hover:bg-green-700
            disabled:opacity-50
          "
        >
          Init Containers
        </button>

        <button
          onClick={onPrint}
          className="
            px-4 py-2 rounded
            bg-blue-600
            hover:bg-blue-700
          "
        >
          Print QR
        </button>

        <button
          onClick={onRegenerate}
          className="
            px-4 py-2 rounded
            bg-yellow-600
            hover:bg-yellow-700
          "
        >
          Regenerate QR
        </button>
      </div>
    </div>
  );
}
