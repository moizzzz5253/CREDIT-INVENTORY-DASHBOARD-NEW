import { useEffect, useState } from "react";
import DashboardLayout from "../layouts/DashboardLayout";
import { getAllComponents, deleteComponent, updateComponent, getCategories } from "../api/components.api";
import { getAllContainers } from "../api/containers.api";
import ComponentCard from "../components/ComponentCard";
import Modal from "../components/Modal";

export default function ManageComponents() {
  const [components, setComponents] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [query, setQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [categories, setCategories] = useState([]);
  const [containers, setContainers] = useState([]);
  const [editing, setEditing] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleteReason, setDeleteReason] = useState("");

  useEffect(() => { load(); loadMeta(); }, []);

  const load = async () => {
    try {
      const data = await getAllComponents();
      setComponents(data || []);
      setFiltered(data || []);
    } catch (e) { console.error(e); }
  };

  const loadMeta = async () => {
    try {
      const [cats, cs] = await Promise.all([getCategories(), getAllContainers()]);
      setCategories(cats || []);
      setContainers(cs || []);
      // default to show all categories
      setCategoryFilter("");
    } catch (e) { console.error(e); }
  };

  useEffect(() => {
    let list = components;
    if (query) list = list.filter(c => c.name.toLowerCase().includes(query.toLowerCase()));
    if (categoryFilter) list = list.filter(c => c.category === categoryFilter);
    setFiltered(list);
  }, [query, categoryFilter, components]);

  const handleDelete = async (component) => {
    // open modal to request delete reason
    setDeleteTarget(component);
    setDeleteReason("");
    setShowDeleteModal(true);
  };

  const handleModify = (component) => {
    // Prefill editing state with full component data
    setEditing({
      id: component.id,
      name: component.name,
      quantity: component.quantity,
      remarks: component.remarks,
      category: component.category,
      container: component.container,
      location: { type: component.location.type, index: component.location.index },
      image: null,
      created_at: component.created_at,
    });
    setShowEditModal(true);
  };

  const saveEdit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        name: editing.name,
        quantity: editing.quantity,
        remarks: editing.remarks,
        category: editing.category,
        container_id: editing.container.id,
        location_type: editing.location.type,
        location_index: editing.location.index,
      };
      if (editing.image) payload.image = editing.image;
      await updateComponent(editing.id, payload);
      setEditing(null);
      setShowEditModal(false);
      await load();
    } catch (err) { alert(err?.response?.data?.detail || 'Update failed'); }
  };

  const confirmDelete = async () => {
    if (!deleteReason || deleteReason.trim() === "") {
      alert("Deletion reason is required");
      return;
    }
    try {
      await deleteComponent(deleteTarget.id, deleteReason);
      setShowDeleteModal(false);
      setDeleteTarget(null);
      await load();
    } catch (e) { alert(e?.response?.data?.detail || 'Delete failed'); }
  };

  return (
    <DashboardLayout title="Manage Components">
      <div className="space-y-4">
        <div className="flex gap-2 items-center">
          <input placeholder="Search by name..." value={query} onChange={(e) => setQuery(e.target.value)} className="flex-1 rounded bg-zinc-900 border border-zinc-700 p-2 text-white" />
          <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)} className="rounded bg-zinc-900 border border-zinc-700 p-2 text-white">
            <option value="">All categories</option>
            {categories.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <a href="/components/add" className="ml-2 px-3 py-2 bg-emerald-600 hover:bg-emerald-700 rounded text-white">Add Component</a>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(c => (
            <ComponentCard key={c.id} component={c} onDelete={handleDelete} onModify={handleModify} onView={() => window.location.href = `/containers/${c.container.code}`} />
          ))}
        </div>

        {filtered.length === 0 && (
          <div className="text-zinc-400">No components found.</div>
        )}

        {editing && (
          <></>
        )}

        {/* Edit modal */}
        <Modal open={showEditModal} title="Modify Component" onClose={() => setShowEditModal(false)}>
          {editing && (
            <form onSubmit={saveEdit} className="space-y-2">
                <label className="text-sm text-zinc-300">Name</label>
                <input value={editing.name} onChange={(e) => setEditing({ ...editing, name: e.target.value })} className="w-full rounded bg-zinc-800 p-2 text-white" />

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-sm text-zinc-300">Quantity</label>
                  <input type="number" value={editing.quantity} onChange={(e) => setEditing({ ...editing, quantity: parseInt(e.target.value, 10) })} className="rounded bg-zinc-800 p-2 text-white" />
                </div>
                <div>
                  <label className="text-sm text-zinc-300">Category</label>
                  <select value={editing.category} onChange={(e) => setEditing({ ...editing, category: e.target.value })} className="rounded bg-zinc-800 p-2 text-white">
                    {categories.map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
              </div>

              <div>
                <label className="text-sm text-zinc-300">Container</label>
                <select value={editing.container.id} onChange={(e) => setEditing({ ...editing, container: containers.find(x => x.id === parseInt(e.target.value,10)) })} className="rounded bg-zinc-800 p-2 text-white">
                  {containers.map(c => <option key={c.id} value={c.id}>{c.code} - {c.cabinet_number}</option>)}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-sm text-zinc-300">Location Type</label>
                  <select value={editing.location.type} onChange={(e) => setEditing({ ...editing, location: { ...editing.location, type: e.target.value, index: editing.location.index } })} className="rounded bg-zinc-800 p-2 text-white">
                    <option value="NONE">None</option>
                    <option value="BOX">BOX</option>
                    <option value="PARTITION">PARTITION</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm text-zinc-300">Location Index</label>
                  <input disabled={editing.location.type === 'NONE'} type="number" min={1} max={15} value={editing.location.index || ''} onChange={(e) => setEditing({ ...editing, location: { ...editing.location, index: e.target.value ? parseInt(e.target.value,10) : null } })} className="rounded bg-zinc-800 p-2 text-white" />
                </div>
              </div>

              <label className="text-sm text-zinc-300">Remarks</label>
              <textarea value={editing.remarks || ''} onChange={(e) => setEditing({ ...editing, remarks: e.target.value })} className="w-full rounded bg-zinc-800 p-2 text-white" />

              <div>
                <label className="text-sm text-zinc-300">Image (optional)</label>
                <input type="file" accept="image/*" onChange={(e) => setEditing({ ...editing, image: e.target.files[0] })} />
              </div>

              <div className="text-zinc-400 text-sm">Date added: {new Date(editing.created_at).toLocaleString()}</div>

              <div className="flex gap-2 mt-2">
                <button type="submit" className="px-3 py-1 bg-emerald-600 rounded text-white">Save</button>
                <button type="button" onClick={() => setShowEditModal(false)} className="px-3 py-1 bg-zinc-700 rounded text-white">Cancel</button>
              </div>
            </form>
          )}
        </Modal>

        {/* Delete modal */}
        <Modal open={showDeleteModal} title={`Delete ${deleteTarget?.name || ''}`} onClose={() => setShowDeleteModal(false)}>
          <div className="space-y-2">
            <p className="text-zinc-300">This action will mark the component as deleted. Please provide a reason (required):</p>
            <input value={deleteReason} onChange={(e) => setDeleteReason(e.target.value)} className="w-full rounded bg-zinc-800 p-2 text-white" />
            <div className="flex gap-2 justify-end">
              <button type="button" onClick={confirmDelete} className="px-3 py-1 bg-red-600 rounded text-white">Delete</button>
              <button type="button" onClick={() => setShowDeleteModal(false)} className="px-3 py-1 bg-zinc-700 rounded text-white">Cancel</button>
            </div>
          </div>
        </Modal>
      </div>
    </DashboardLayout>
  );
}
