import { useEffect, useState } from "react";
import { createComponent } from "../../api/components.api";
import { getAllContainers } from "../../api/containers.api";
import { CATEGORIES } from "./categories";
import Button from "../ui/Button";

export default function AddComponentForm({ onSuccess }) {
  const [containers, setContainers] = useState([]);
  const [form, setForm] = useState({
    name: "",
    category: "",
    quantity: 1,
    container_id: "",
    remarks: "",
    image: null,
  });

  useEffect(() => {
    getAllContainers().then(setContainers);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const data = new FormData();
    Object.entries(form).forEach(([k, v]) => v && data.append(k, v));

    await createComponent(data);
    onSuccess();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-zinc-800 p-6 rounded-lg">
      <h3 className="text-lg font-semibold">Add Component</h3>

      <input
        className="w-full p-2 rounded bg-zinc-700"
        placeholder="Component Name"
        value={form.name}
        onChange={(e) => setForm({ ...form, name: e.target.value })}
        required
      />

      <select
        className="w-full p-2 rounded bg-zinc-700"
        value={form.category}
        onChange={(e) => setForm({ ...form, category: e.target.value })}
        required
      >
        <option value="">Select Category</option>
        {CATEGORIES.map((c) => (
          <option key={c}>{c}</option>
        ))}
      </select>

      <select
        className="w-full p-2 rounded bg-zinc-700"
        value={form.container_id}
        onChange={(e) =>
          setForm({ ...form, container_id: e.target.value })
        }
        required
      >
        <option value="">Select Container</option>
        {containers.map((c) => (
          <option key={c.id} value={c.id}>
            {c.code}
          </option>
        ))}
      </select>

      <input
        type="number"
        min="0"
        className="w-full p-2 rounded bg-zinc-700"
        value={form.quantity}
        onChange={(e) => setForm({ ...form, quantity: e.target.value })}
      />

      <textarea
        className="w-full p-2 rounded bg-zinc-700"
        placeholder="Remarks (optional)"
        value={form.remarks}
        onChange={(e) => setForm({ ...form, remarks: e.target.value })}
      />

      <input
        type="file"
        accept="image/*"
        onChange={(e) => setForm({ ...form, image: e.target.files[0] })}
        required
      />

      <Button type="submit">Add Component</Button>
    </form>
  );
}
