import React, { useEffect, useState } from "react";
import { getAllContainers } from "../api/containers.api";
import { getCategories, createComponent } from "../api/components.api";

export default function AddComponent() {
  const [containers, setContainers] = useState([]);
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState({
    name: "",
    quantity: 1,
    remarks: "",
    category: "",
    container_id: null,
    location_type: "NONE",
    location_index: "",
    image: null,
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    loadMeta();
  }, []);

  const loadMeta = async () => {
    try {
      const [cs, cats] = await Promise.all([getAllContainers(), getCategories()]);
      setContainers(cs || []);
      setCategories(cats || []);
      if (cats && cats.length) setForm((f) => ({ ...f, category: cats[0] }));
      if (cs && cs.length) setForm((f) => ({ ...f, container_id: cs[0].id }));
    } catch (e) {
      console.error(e);
    }
  };

  const handleChange = (k, v) => setForm((s) => ({ ...s, [k]: v }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSuccess(null);
    try {
      const payload = {
        name: form.name,
        quantity: parseInt(form.quantity, 10),
        remarks: form.remarks || undefined,
        category: form.category,
        container_id: form.container_id,
        location_type: form.location_type,
        location_index: form.location_type === "NONE" ? undefined : parseInt(form.location_index, 10),
        image: form.image,
      };

      const res = await createComponent(payload);
      setSuccess(res);
      setForm({ name: "", quantity: 1, remarks: "", category: categories[0] || "", container_id: containers[0]?.id || null, location_type: "NONE", location_index: "", image: null });
    } catch (err) {
      console.error(err);
      alert(err?.response?.data?.detail || "Failed to create component");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-zinc-300">Name</label>
            <input required value={form.name} onChange={(e) => handleChange('name', e.target.value)} className="mt-1 block w-full rounded bg-zinc-900 border border-zinc-700 p-2 text-white" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-zinc-300">Quantity</label>
              <input required type="number" min={1} value={form.quantity} onChange={(e) => handleChange('quantity', e.target.value)} className="mt-1 block w-full rounded bg-zinc-900 border border-zinc-700 p-2 text-white" />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-300">Category</label>
              <select required value={form.category} onChange={(e) => handleChange('category', e.target.value)} className="mt-1 block w-full rounded bg-zinc-900 border border-zinc-700 p-2 text-white">
                {categories.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-300">Container</label>
            <select required value={form.container_id || ""} onChange={(e) => handleChange('container_id', parseInt(e.target.value, 10))} className="mt-1 block w-full rounded bg-zinc-900 border border-zinc-700 p-2 text-white">
              {containers.map(c => <option key={c.id} value={c.id}>{c.code} - {c.cabinet_number}</option>)}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-zinc-300">Location Type (optional)</label>
              <select value={form.location_type} onChange={(e) => handleChange('location_type', e.target.value)} className="mt-1 block w-full rounded bg-zinc-900 border border-zinc-700 p-2 text-white">
                <option value="NONE">None</option>
                <option value="BOX">BOX</option>
                <option value="PARTITION">PARTITION</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-300">Location Index (1-15)</label>
              <input disabled={form.location_type === 'NONE'} type="number" min={1} max={15} value={form.location_index} onChange={(e) => handleChange('location_index', e.target.value)} className="mt-1 block w-full rounded bg-zinc-900 border border-zinc-700 p-2 text-white" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-300">Remarks (optional)</label>
            <textarea value={form.remarks} onChange={(e) => handleChange('remarks', e.target.value)} className="mt-1 block w-full rounded bg-zinc-900 border border-zinc-700 p-2 text-white" />
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-300">Image (optional)</label>
            <input type="file" accept="image/*" onChange={(e) => handleChange('image', e.target.files[0])} className="mt-1 block w-full text-white" />
            <p className="text-zinc-500 text-sm mt-1">If no image is provided, a placeholder will be used.</p>
          </div>

          <div className="flex items-center space-x-2">
            <button disabled={loading} type="submit" className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 rounded text-white">Add Component</button>
          </div>
        </form>

        {success && (
          <div className="mt-6 bg-zinc-900 border border-emerald-700 rounded p-4">
            <h4 className="font-semibold text-emerald-300">Component added successfully</h4>
            <p className="text-zinc-300">Name: {success.name}</p>
            <p className="text-zinc-300">Category: {success.category}</p>
            <p className="text-zinc-300">Qty: {success.quantity}</p>
            <p className="text-zinc-300">Container: {success.container?.code || success.location?.label}</p>
            <p className="text-zinc-300">Location: {success.location?.type && success.location.type !== 'NONE' ? `${success.location.type} ${success.location.index}` : 'None'}</p>
            <p className="text-zinc-300">Added: {success.created_at ? new Date(success.created_at).toLocaleString() : 'Unknown'}</p>
          </div>
        )}
      </div>
  );
}
