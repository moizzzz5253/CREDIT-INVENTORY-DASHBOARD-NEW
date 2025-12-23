import { useState, useEffect } from "react";
import { updateComponent, updateComponentImage } from "../../api/components.api";
import { getAllContainers } from "../../api/containers.api";
import { CATEGORIES } from "../../components/components/categories";

export default function ModifyComponentModal({ component, onClose, onUpdated }) {
  const [form, setForm] = useState({
    name: "",
    category: "",
    container_id: null,
    quantity: 0,
    remarks: "",
  });

  const [containers, setContainers] = useState([]);
  const [imageFile, setNewImage] = useState(null);


  useEffect(() => {
    // Autofill form
    setForm({
      name: component.name,
      category: component.category,
      container_id: component.container.id,
      quantity: component.quantity,
      remarks: component.remarks || "",
    });

    getAllContainers().then(setContainers);
  }, [component]);

  const handleChange = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

const submit = async () => {
  const payload = {
    name: form.name,
    category: form.category || component.category,
    quantity: form.quantity,
    remarks: form.remarks,
    container_id: form.container_id ?? component.container.id,
  };

  // 1️⃣ Update component fields
  await updateComponent(component.id, payload);

  // 2️⃣ Update image if provided
  if (imageFile) {
    const formData = new FormData();
    formData.append("image", imageFile);
    await updateComponentImage(component.id, formData);
  }

  onUpdated();
};




  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
  <div className="bg-zinc-900 p-6 rounded w-105">
    <h2 className="text-lg font-semibold mb-4">Modify Component</h2>

    {/* NAME */}
    <label className="block mb-2">Name</label>
    <input
      className="w-full p-2 bg-zinc-800 rounded mb-3"
      value={form.name ?? ""}
      onChange={(e) => handleChange("name", e.target.value)}
    />

    {/* CATEGORY */}
    <label className="block mb-2">Category</label>
    <select
      className="w-full p-2 bg-zinc-800 rounded mb-3"
      value={form.category ?? ""}
      onChange={(e) => handleChange("category", e.target.value)}
    >
      {CATEGORIES.map((c) => (
        <option key={c} value={c}>
          {c}
        </option>
      ))}
    </select>

    {/* CONTAINER */}
    <label className="block mb-2">Container</label>
    <select
      className="w-full p-2 bg-zinc-800 rounded mb-1 disabled:opacity-50"
      value={form.container_id ?? ""}
      onChange={(e) =>
        handleChange("container_id", Number(e.target.value))
      }
      disabled={component.borrowed_quantity > 0}
    >
      {containers.map((c) => (
        <option key={c.id} value={c.id}>
          {c.code}
        </option>
      ))}
    </select>

    {component.borrowed_quantity > 0 && (
      <p className="text-sm text-red-400 mt-1">
        Container cannot be changed while component is borrowed
      </p>
    )}

    {/* QUANTITY */}
    <label className="block mb-2 mt-3">Quantity (Global)</label>
    <div className="flex gap-2 mb-3">
      <button
        type="button"
        className="px-3 bg-zinc-700 rounded"
        onClick={() =>
          handleChange(
            "quantity",
            Math.max(
              component.borrowed_quantity,
              form.quantity - 1
            )
          )
        }
      >
        −
      </button>

      <input
        type="number"
        min={component.borrowed_quantity}
        className="flex-1 p-2 bg-zinc-800 rounded"
        value={form.quantity ?? 0}
        onChange={(e) =>
          handleChange(
            "quantity",
            Number(e.target.value)
          )
        }
      />

      <button
        type="button"
        className="px-3 bg-zinc-700 rounded"
        onClick={() =>
          handleChange("quantity", form.quantity + 1)
        }
      >
        +
      </button>
    </div>

    <div className="text-sm text-zinc-400 mb-3">
      Borrowed: {component.borrowed_quantity} | Available:{" "}
      {component.available_quantity}
    </div>

    {/* REMARKS */}
    <label className="block mb-2">Remarks</label>
    <textarea
      className="w-full p-2 bg-zinc-800 rounded mb-4"
      value={form.remarks ?? ""}
      onChange={(e) => handleChange("remarks", e.target.value)}
    />

    {/* IMAGE */}
    <label className="block mb-2">Replace Image (optional)</label>
    <input
      type="file"
      accept="image/*"
      className="w-full p-2 bg-zinc-800 rounded mb-4"
      onChange={(e) =>
        setNewImage(e.target.files?.[0] ?? null)
      }
    />

    {/* ACTIONS */}
    <div className="flex justify-end gap-3">
      <button
        type="button"
        onClick={onClose}
        className="px-4 py-2 bg-zinc-700 rounded"
      >
        Cancel
      </button>
      <button
        type="button"
        onClick={submit}
        className="px-4 py-2 bg-blue-600 rounded"
      >
        Save
      </button>
    </div>
  </div>
</div>

  );
}
