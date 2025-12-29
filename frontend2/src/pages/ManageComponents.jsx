import React, { useEffect, useState } from "react";
import { getAllComponents, deleteComponent, updateComponent, getCategories } from "../api/components.api";
import { getAllContainers } from "../api/containers.api";
import ComponentCard from "../components/ComponentCard";
import Modal from "../components/Modal";
import StorageLocationForm from "../components/StorageLocationForm";

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
    // Prefill editing state with full component data including new storage fields
    setEditing({
      id: component.id,
      name: component.name,
      quantity: component.quantity,
      remarks: component.remarks || "",
      category: component.category,
      storage_type: component.storage_type || "CABINET",
      cabinet_number: component.cabinet_number || null,
      shelf_number: component.shelf_number !== undefined ? component.shelf_number : null,
      container_id: component.container?.id || null,
      drawer_index: component.drawer_index || null,
      storage_box_index: component.storage_box_index || null,
      location_type: component.location?.type || "NONE",
      location_index: component.location?.index || null,
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
        storage_type: editing.storage_type,
        cabinet_number: editing.cabinet_number,
        shelf_number: editing.shelf_number,
        container_id: editing.container_id || undefined,
        drawer_index: editing.drawer_index,
        storage_box_index: editing.storage_box_index,
        location_type: editing.location_type,
        location_index: editing.location_type !== "NONE" ? editing.location_index : undefined,
      };
      if (editing.image) payload.image = editing.image;
      await updateComponent(editing.id, payload);
      setEditing(null);
      setShowEditModal(false);
      await load();
    } catch (err) { alert(err?.response?.data?.detail || 'Update failed'); }
  };
  
  const handleEditingChange = (field, value) => {
    setEditing((prev) => {
      const newEditing = { ...prev, [field]: value };
      
      // Reset dependent fields when storage_type changes
      if (field === "storage_type") {
        if (value === "CABINET") {
          newEditing.drawer_index = null;
          newEditing.storage_box_index = null;
        } else if (value === "DRAWER") {
          newEditing.cabinet_number = null;
          newEditing.shelf_number = null;
          newEditing.container_id = null;
        } else if (value === "STORAGE_BOX") {
          newEditing.cabinet_number = null;
          newEditing.shelf_number = null;
          newEditing.container_id = null;
          newEditing.drawer_index = null;
          newEditing.location_type = "NONE";
          newEditing.location_index = null;
        }
      }
      
      // Reset container_id when cabinet_number changes
      if (field === "cabinet_number") {
        newEditing.container_id = null;
      }
      
      // Reset location_type/index when container_id is cleared or shelf is 0
      if (field === "container_id" && !value) {
        newEditing.location_type = "NONE";
        newEditing.location_index = null;
      }
      if (field === "shelf_number" && value === 0) {
        newEditing.container_id = null;
        newEditing.location_type = "NONE";
        newEditing.location_index = null;
      }
      
      return newEditing;
    });
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

              {/* Storage Location Form */}
              <StorageLocationForm
                storageType={editing.storage_type}
                cabinetNumber={editing.cabinet_number}
                shelfNumber={editing.shelf_number}
                containerId={editing.container_id}
                drawerIndex={editing.drawer_index}
                storageBoxIndex={editing.storage_box_index}
                locationType={editing.location_type}
                locationIndex={editing.location_index}
                containers={containers}
                onStorageTypeChange={(v) => handleEditingChange('storage_type', v)}
                onCabinetNumberChange={(v) => handleEditingChange('cabinet_number', v)}
                onShelfNumberChange={(v) => handleEditingChange('shelf_number', v)}
                onContainerIdChange={(v) => handleEditingChange('container_id', v)}
                onDrawerIndexChange={(v) => handleEditingChange('drawer_index', v)}
                onStorageBoxIndexChange={(v) => handleEditingChange('storage_box_index', v)}
                onLocationTypeChange={(v) => handleEditingChange('location_type', v)}
                onLocationIndexChange={(v) => handleEditingChange('location_index', v)}
              />

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
  );
}
