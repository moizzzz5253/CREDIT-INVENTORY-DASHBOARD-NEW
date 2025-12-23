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

    // 🔑 NEW (optional location)
    location_type: "NONE", // NONE | BOX | PARTITION
    location_index: "",
  });

  useEffect(() => {
    getAllContainers().then(setContainers);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const data = new FormData();

    // 🔒 Explicit append (NO silent drops)
    data.append("name", form.name);
    data.append("category", form.category);
    data.append("quantity", Number(form.quantity));
    data.append("container_id", Number(form.container_id));

    if (form.remarks) {
      data.append("remarks", form.remarks);
    }

    data.append("location_type", form.location_type);

    if (form.location_type !== "NONE") {
      data.append("location_index", Number(form.location_index));
    }

    if (!form.image) {
      alert("Image is required");
      return;
    }

    data.append("image", form.image);

    await createComponent(data);
    onSuccess();
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 bg-zinc-800 p-6 rounded-lg"
    >
      <h3 className="text-lg font-semibold">Add Component</h3>

      {/* NAME */}
      <input
        className="w-full p-2 rounded bg-zinc-700"
        placeholder="Component Name"
        value={form.name}
        onChange={(e) =>
          setForm({ ...form, name: e.target.value })
        }
        required
      />

      {/* CATEGORY */}
      <select
        className="w-full p-2 rounded bg-zinc-700"
        value={form.category}
        onChange={(e) =>
          setForm({ ...form, category: e.target.value })
        }
        required
      >
        <option value="">Select Category</option>
        {CATEGORIES.map((c) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </select>

      {/* CONTAINER */}
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

      {/* LOCATION TYPE */}
      <select
        className="w-full p-2 rounded bg-zinc-700"
        value={form.location_type}
        onChange={(e) =>
          setForm({
            ...form,
            location_type: e.target.value,
            location_index: "",
          })
        }
      >
        <option value="NONE">No Box / Partition</option>
        <option value="BOX">Box</option>
        <option value="PARTITION">Partition</option>
      </select>

      {/* LOCATION INDEX */}
      {form.location_type !== "NONE" && (
        <input
          type="number"
          min="1"
          max="15"
          className="w-full p-2 rounded bg-zinc-700"
          placeholder={
            form.location_type === "BOX"
              ? "Box number (1–15)"
              : "Partition number (1–15)"
          }
          value={form.location_index}
          onChange={(e) =>
            setForm({
              ...form,
              location_index: e.target.value,
            })
          }
          required
        />
      )}

      {/* QUANTITY */}
      <input
        type="number"
        min="0"
        className="w-full p-2 rounded bg-zinc-700"
        value={form.quantity}
        onChange={(e) =>
          setForm({ ...form, quantity: e.target.value })
        }
        required
      />

      {/* REMARKS */}
      <textarea
        className="w-full p-2 rounded bg-zinc-700"
        placeholder="Remarks (optional)"
        value={form.remarks}
        onChange={(e) =>
          setForm({ ...form, remarks: e.target.value })
        }
      />

      {/* IMAGE */}
      <input
        type="file"
        accept="image/*"
        onChange={(e) =>
          setForm({ ...form, image: e.target.files[0] })
        }
        required
      />

      <Button type="submit">Add Component</Button>
    </form>
  );
}
