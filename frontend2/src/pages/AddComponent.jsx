import React, { useEffect, useState } from "react";
import { getAllContainers } from "../api/containers.api";
import { getCategories, createComponent } from "../api/components.api";
import { verifyAdminPassword } from "../api/admin.api";
import StorageLocationForm from "../components/StorageLocationForm";

export default function AddComponent() {
  const [containers, setContainers] = useState([]);
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState({
    name: "",
    quantity: 1,
    remarks: "",
    category: "",
    storage_type: "CABINET",
    cabinet_number: null,
    shelf_number: null,
    container_id: null,
    drawer_index: null,
    storage_box_index: null,
    location_type: "NONE",
    location_index: null,
    image: null,
    is_controlled: false,
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [adminPassword, setAdminPassword] = useState("");
  const [passwordError, setPasswordError] = useState("");

  useEffect(() => {
    loadMeta();
  }, []);

  const loadMeta = async () => {
    try {
      const [cs, cats] = await Promise.all([getAllContainers(), getCategories()]);
      setContainers(cs || []);
      setCategories(cats || []);
      if (cats && cats.length) setForm((f) => ({ ...f, category: cats[0] }));
      if (cs && cs.length) {
        // Set default to first cabinet and first container
        const firstCabinet = cs[0]?.cabinet_number || 1;
        const firstContainer = cs.find(c => c.cabinet_number === firstCabinet);
        setForm((f) => ({ 
          ...f, 
          cabinet_number: firstCabinet,
          shelf_number: 1,
          container_id: firstContainer?.id || null
        }));
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleChange = (k, v) => {
    setForm((s) => {
      const newForm = { ...s, [k]: v };
      
      // Reset dependent fields when storage_type changes
      if (k === "storage_type") {
        if (v === "CABINET") {
          newForm.drawer_index = null;
          newForm.storage_box_index = null;
        } else if (v === "DRAWER") {
          newForm.cabinet_number = null;
          newForm.shelf_number = null;
          newForm.container_id = null;
        } else if (v === "STORAGE_BOX") {
          newForm.cabinet_number = null;
          newForm.shelf_number = null;
          newForm.container_id = null;
          newForm.drawer_index = null;
          newForm.location_type = "NONE";
          newForm.location_index = null;
        }
      }
      
      // Reset container_id when cabinet_number changes
      if (k === "cabinet_number") {
        newForm.container_id = null;
      }
      
      // Reset location_type/index when container_id is cleared or shelf is 0
      if (k === "container_id" && !v) {
        newForm.location_type = "NONE";
        newForm.location_index = null;
      }
      if (k === "shelf_number" && v === 0) {
        newForm.container_id = null;
        newForm.location_type = "NONE";
        newForm.location_index = null;
      }
      
      return newForm;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Prevent double submission
    if (loading) {
      return;
    }
    
    // If controlled, show password modal first
    if (form.is_controlled) {
      setShowPasswordModal(true);
      return;
    }
    
    await submitComponent();
  };

  const handlePasswordSubmit = async (e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    
    if (!adminPassword.trim()) {
      setPasswordError("Password is required");
      return;
    }

    try {
      const result = await verifyAdminPassword(adminPassword);
      if (result.success) {
        setPasswordError("");
        setShowPasswordModal(false);
        await submitComponent(adminPassword);
      } else {
        setPasswordError(result.message || "Invalid password");
      }
    } catch (err) {
      setPasswordError(err?.response?.data?.message || "Failed to verify password");
    }
  };

  const submitComponent = async (password = null) => {
    // Prevent double submission
    if (loading) {
      return;
    }
    
    setLoading(true);
    setSuccess(null);
    try {
      const payload = {
        name: form.name,
        quantity: parseInt(form.quantity, 10),
        remarks: form.remarks || undefined,
        category: form.category,
        storage_type: form.storage_type,
        cabinet_number: form.cabinet_number,
        shelf_number: form.shelf_number,
        container_id: form.container_id || undefined,
        drawer_index: form.drawer_index,
        storage_box_index: form.storage_box_index,
        location_type: form.location_type,
        location_index: form.location_type !== "NONE" ? form.location_index : undefined,
        image: form.image,
        is_controlled: form.is_controlled,
        admin_password: password || undefined,
      };

      const res = await createComponent(payload);
      setSuccess(res);
      
      // Reset form to defaults
      const firstCabinet = containers[0]?.cabinet_number || 1;
      const firstContainer = containers.find(c => c.cabinet_number === firstCabinet);
      setForm({ 
        name: "", 
        quantity: 1, 
        remarks: "", 
        category: categories[0] || "",
        storage_type: "CABINET",
        cabinet_number: firstCabinet,
        shelf_number: 1,
        container_id: firstContainer?.id || null,
        drawer_index: null,
        storage_box_index: null,
        location_type: "NONE", 
        location_index: null,
        image: null,
        is_controlled: false,
      });
      setAdminPassword("");
      setPasswordError("");
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

          {/* Storage Location Form */}
          <StorageLocationForm
            storageType={form.storage_type}
            cabinetNumber={form.cabinet_number}
            shelfNumber={form.shelf_number}
            containerId={form.container_id}
            drawerIndex={form.drawer_index}
            storageBoxIndex={form.storage_box_index}
            locationType={form.location_type}
            locationIndex={form.location_index}
            containers={containers}
            onStorageTypeChange={(v) => handleChange('storage_type', v)}
            onCabinetNumberChange={(v) => handleChange('cabinet_number', v)}
            onShelfNumberChange={(v) => handleChange('shelf_number', v)}
            onContainerIdChange={(v) => handleChange('container_id', v)}
            onDrawerIndexChange={(v) => handleChange('drawer_index', v)}
            onStorageBoxIndexChange={(v) => handleChange('storage_box_index', v)}
            onLocationTypeChange={(v) => handleChange('location_type', v)}
            onLocationIndexChange={(v) => handleChange('location_index', v)}
          />

          <div>
            <label className="block text-sm font-medium text-zinc-300">Remarks (optional)</label>
            <textarea value={form.remarks} onChange={(e) => handleChange('remarks', e.target.value)} className="mt-1 block w-full rounded bg-zinc-900 border border-zinc-700 p-2 text-white" />
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-300">Image (optional)</label>
            <input type="file" accept="image/*" onChange={(e) => handleChange('image', e.target.files[0])} className="mt-1 block w-full text-white" />
            <p className="text-zinc-500 text-sm mt-1">If no image is provided, a placeholder will be used.</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-300">Controlled Item</label>
            <select 
              value={form.is_controlled ? "yes" : "no"} 
              onChange={(e) => handleChange('is_controlled', e.target.value === "yes")} 
              className="mt-1 block w-full rounded bg-zinc-900 border border-zinc-700 p-2 text-white"
            >
              <option value="no">No</option>
              <option value="yes">Yes (Cannot be borrowed)</option>
            </select>
            <p className="text-zinc-500 text-sm mt-1">Controlled items cannot be borrowed and require admin authorization.</p>
          </div>

          <div className="flex items-center space-x-2">
            <button disabled={loading} type="submit" className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 rounded text-white">Add Component</button>
          </div>
        </form>

        {/* Password Modal */}
        {showPasswordModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-zinc-800 p-6 rounded-lg border border-zinc-700 max-w-md w-full">
              <h3 className="text-lg font-semibold text-white mb-4">Admin Password Required</h3>
              <p className="text-zinc-300 mb-4">This component is marked as controlled. Please enter the admin password to proceed.</p>
              <input
                type="password"
                value={adminPassword}
                onChange={(e) => {
                  setAdminPassword(e.target.value);
                  setPasswordError("");
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handlePasswordSubmit();
                  }
                }}
                placeholder="Enter admin password"
                className="w-full p-2 bg-zinc-900 border border-zinc-700 rounded text-white mb-2"
                autoFocus
              />
              {passwordError && (
                <p className="text-red-400 text-sm mb-2">{passwordError}</p>
              )}
              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => {
                    setShowPasswordModal(false);
                    setAdminPassword("");
                    setPasswordError("");
                  }}
                  className="px-4 py-2 bg-zinc-700 hover:bg-zinc-600 rounded text-white"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handlePasswordSubmit}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 rounded text-white"
                >
                  Submit
                </button>
              </div>
            </div>
          </div>
        )}

        {success && (
          <div className="mt-6 bg-zinc-900 border border-emerald-700 rounded p-4">
            <h4 className="font-semibold text-emerald-300">Component added successfully</h4>
            <p className="text-zinc-300">Name: {success.name}</p>
            <p className="text-zinc-300">Category: {success.category}</p>
            <p className="text-zinc-300">Qty: {success.quantity}</p>
            <p className="text-zinc-300">Location: {success.location?.label || 'Unknown'}</p>
            <p className="text-zinc-300">Added: {success.created_at ? new Date(success.created_at).toLocaleString() : 'Unknown'}</p>
          </div>
        )}
      </div>
  );
}
