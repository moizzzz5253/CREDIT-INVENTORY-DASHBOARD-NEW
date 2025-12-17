import Select from "react-select";

export default function BorrowItemRow({
  components,
  item,
  onChange,
  onRemove,
}) {
  const options = components.map((c) => ({
    value: c.id,
    label: `${c.name} (Available: ${c.quantity})`,
  }));

  return (
    <div className="grid grid-cols-6 gap-2 items-center">
      <div className="col-span-3">
        <Select
          options={options}
          value={options.find(o => o.value === item.component_id) || null}
          onChange={(opt) =>
            onChange({ ...item, component_id: opt.value })
          }
          placeholder="Search component..."
        />
      </div>

      <input
        type="number"
        min="1"
        className="bg-zinc-800 p-2 rounded"
        value={item.quantity}
        onChange={(e) =>
          onChange({ ...item, quantity: Number(e.target.value) })
        }
        required
      />

      <button
        type="button"
        onClick={onRemove}
        className="text-red-400 hover:text-red-600"
      >
        ✕
      </button>
    </div>
  );
}