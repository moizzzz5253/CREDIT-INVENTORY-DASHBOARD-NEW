import React, { useState, useEffect } from 'react';
import {
  downloadImportTemplate,
  validateExcelImport,
  finalizeComponentImport,
  uploadComponentImage,
  exportComponentsReport
} from '../api/import.api.js';
import {
  exportFullDatabase,
  restructureDatabase,
  previewRestructure,
  restructureFromExcel
} from '../api/database.api.js';

export default function SystemManager() {
  const [activeTab, setActiveTab] = useState('import'); // 'import', 'export', or 'database'
  const [excelFile, setExcelFile] = useState(null);
  const [validatedComponents, setValidatedComponents] = useState([]);
  const [errors, setErrors] = useState([]);
  const [componentImages, setComponentImages] = useState({}); // index -> File object
  const [imagePreviewUrls, setImagePreviewUrls] = useState({}); // index -> preview URL
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState(''); // 'success' or 'error'

  // Get preview URL for image (with cleanup)
  const getImagePreview = (index, file) => {
    if (!file) {
      // Clean up old URL if exists
      if (imagePreviewUrls[index]) {
        URL.revokeObjectURL(imagePreviewUrls[index]);
        setImagePreviewUrls(prev => {
          const newUrls = { ...prev };
          delete newUrls[index];
          return newUrls;
        });
      }
      return null;
    }
    
    // Clean up old URL if exists
    if (imagePreviewUrls[index]) {
      URL.revokeObjectURL(imagePreviewUrls[index]);
    }
    
    const url = URL.createObjectURL(file);
    setImagePreviewUrls(prev => ({ ...prev, [index]: url }));
    return url;
  };

  // Cleanup preview URLs on unmount
  useEffect(() => {
    return () => {
      Object.values(imagePreviewUrls).forEach(url => {
        URL.revokeObjectURL(url);
      });
    };
  }, [imagePreviewUrls]);

  // Handle Excel file selection
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.name.endsWith('.xlsx')) {
        setMessage('Please select an Excel (.xlsx) file');
        setMessageType('error');
        return;
      }
      setExcelFile(file);
      setValidatedComponents([]);
      setErrors([]);
      setComponentImages({});
      // Clean up all preview URLs
      Object.values(imagePreviewUrls).forEach(url => URL.revokeObjectURL(url));
      setImagePreviewUrls({});
      setMessage('');
    }
  };

  // Validate Excel file
  const handleValidate = async () => {
    if (!excelFile) {
      setMessage('Please select an Excel file first');
      setMessageType('error');
      return;
    }

    setLoading(true);
    setMessage('');
    setMessageType('');

    try {
      const result = await validateExcelImport(excelFile);
      setValidatedComponents(result.components || []);
      setErrors(result.errors || []);

      if (result.errors && result.errors.length > 0) {
        setMessage(`Validation found ${result.errors.length} error(s). Please fix them before proceeding.`);
        setMessageType('error');
      } else {
        setMessage(`Validation successful! ${result.components?.length || 0} component(s) ready to import.`);
        setMessageType('success');
      }
    } catch (error) {
      setMessage(error.message || 'Error validating Excel file');
      setMessageType('error');
      setValidatedComponents([]);
      setErrors([]);
    } finally {
      setLoading(false);
    }
  };

  // Handle image selection for a component
  const handleImageChange = (index, file) => {
    setComponentImages(prev => ({
      ...prev,
      [index]: file
    }));
    // Generate preview URL
    if (file) {
      getImagePreview(index, file);
    }
  };

  // Remove image for a component
  const handleRemoveImage = (index) => {
    setComponentImages(prev => {
      const newImages = { ...prev };
      delete newImages[index];
      return newImages;
    });
    getImagePreview(index, null); // Clean up preview URL
  };

  // Finalize import
  const handleSubmit = async () => {
    if (validatedComponents.length === 0) {
      setMessage('No components to import. Please validate Excel file first.');
      setMessageType('error');
      return;
    }

    setLoading(true);
    setMessage('');
    setMessageType('');

    try {
      // Step 1: Create components
      const result = await finalizeComponentImport(validatedComponents);
      
      // Step 2: Upload images for components that have them
      // Map component IDs to original indices
      const componentIdMap = {}; // originalIndex -> componentId
      result.components.forEach(createdComp => {
        if (createdComp.index !== undefined) {
          componentIdMap[createdComp.index] = createdComp.id;
        }
      });

      const imageUploadPromises = [];
      Object.keys(componentImages).forEach(originalIndex => {
        const componentId = componentIdMap[parseInt(originalIndex)];
        const imageFile = componentImages[originalIndex];
        if (componentId && imageFile) {
          imageUploadPromises.push(
            uploadComponentImage(componentId, imageFile).catch(err => {
              console.error(`Error uploading image for component ${componentId}:`, err);
              return null; // Continue with other uploads even if one fails
            })
          );
        }
      });

      // Upload all images in parallel
      if (imageUploadPromises.length > 0) {
        await Promise.all(imageUploadPromises);
      }

      setMessage(`Successfully imported ${result.inserted} component(s) into the inventory!`);
      setMessageType('success');

      // Reset form
      setTimeout(() => {
        setExcelFile(null);
        setValidatedComponents([]);
        setErrors([]);
        setComponentImages({});
        setMessage('');
        setMessageType('');
        // Reset file input
        const fileInput = document.getElementById('excel-file-input');
        if (fileInput) fileInput.value = '';
      }, 3000);

    } catch (error) {
      setMessage(error.message || 'Error importing components');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  // Handle export
  const handleExport = async () => {
    setLoading(true);
    setMessage('');
    setMessageType('');

    try {
      await exportComponentsReport();
      setMessage('Components report exported successfully!');
      setMessageType('success');
    } catch (error) {
      setMessage(error.message || 'Error exporting report');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-zinc-900 text-zinc-200 min-h-screen">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">System Manager</h1>
      </div>

      {/* Tabs */}
      <div className="flex space-x-4 mb-6 border-b border-zinc-700">
        <button
          onClick={() => {
            setActiveTab('import');
            setMessage('');
            setMessageType('');
          }}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'import'
              ? 'text-white border-b-2 border-blue-500'
              : 'text-zinc-400 hover:text-white'
          }`}
        >
          Import Components
        </button>
        <button
          onClick={() => {
            setActiveTab('export');
            setMessage('');
            setMessageType('');
          }}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'export'
              ? 'text-white border-b-2 border-blue-500'
              : 'text-zinc-400 hover:text-white'
          }`}
        >
          Export Report
        </button>
        <button
          onClick={() => {
            setActiveTab('database');
            setMessage('');
            setMessageType('');
          }}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'database'
              ? 'text-white border-b-2 border-blue-500'
              : 'text-zinc-400 hover:text-white'
          }`}
        >
          Database Management
        </button>
      </div>

      {activeTab === 'import' && (
        <div className="space-y-6">
          {/* Instructions */}
          <div className="bg-zinc-800 p-6 rounded-lg border border-zinc-700">
            <h2 className="text-xl font-semibold mb-4">How to Import Components</h2>
            <div className="space-y-3 text-zinc-300">
              <p>1. Download the Excel template below to see the required format</p>
              <p>2. Fill in the template with your component data</p>
              <p>3. Upload the filled Excel file</p>
              <p>4. Review and add images for each component (optional)</p>
              <p>5. Submit to import all components</p>
            </div>

            <div className="mt-4 p-4 bg-zinc-900 rounded border border-zinc-600">
              <h3 className="font-semibold mb-2">Required Columns:</h3>
              <ul className="list-disc list-inside space-y-1 text-sm text-zinc-300">
                <li><strong>name</strong> - Component name (required)</li>
                <li><strong>category</strong> - Component category (required)</li>
                <li><strong>quantity</strong> - Quantity available (required)</li>
                <li><strong>container_code</strong> - Container code e.g., A1, B2 (required)</li>
                <li><strong>location_type</strong> - NONE, BOX, or PARTITION (optional, default: NONE)</li>
                <li><strong>location_index</strong> - Location index 1-15 (required if location_type is not NONE)</li>
                <li><strong>remarks</strong> - Additional remarks (optional)</li>
              </ul>
            </div>

            <button
              onClick={downloadImportTemplate}
              className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white transition-colors"
            >
              Download Excel Template
            </button>
          </div>

          {/* File Upload */}
          <div className="bg-zinc-800 p-6 rounded-lg border border-zinc-700">
            <h2 className="text-xl font-semibold mb-4">Upload Excel File</h2>
            <div className="space-y-4">
              <div>
                <input
                  id="excel-file-input"
                  type="file"
                  accept=".xlsx"
                  onChange={handleFileChange}
                  className="block w-full text-sm text-zinc-300 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700"
                />
                {excelFile && (
                  <p className="mt-2 text-zinc-400 text-sm">Selected: {excelFile.name}</p>
                )}
              </div>
              <button
                onClick={handleValidate}
                disabled={!excelFile || loading}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Validating...' : 'Validate Excel File'}
              </button>
            </div>
          </div>

          {/* Errors */}
          {errors.length > 0 && (
            <div className="bg-red-900/50 border border-red-600 p-4 rounded-lg">
              <h3 className="font-semibold text-red-400 mb-2">Validation Errors:</h3>
              <ul className="space-y-1">
                {errors.map((error, idx) => (
                  <li key={idx} className="text-red-300 text-sm">
                    Row {error.row}: {error.error}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Components List */}
          {validatedComponents.length > 0 && (
            <div className="bg-zinc-800 p-6 rounded-lg border border-zinc-700">
              <h2 className="text-xl font-semibold mb-4">
                Components to Import ({validatedComponents.length})
              </h2>
              <div className="space-y-4">
                {validatedComponents.map((comp, idx) => {
                  const imagePreview = imagePreviewUrls[idx] || null;
                  const locationDisplay = comp.location_type === 'NONE' 
                    ? 'N/A' 
                    : `${comp.location_type} ${comp.location_index}`;

                  return (
                    <div
                      key={idx}
                      className="bg-zinc-900 p-4 rounded border border-zinc-600"
                    >
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="md:col-span-2 space-y-2">
                          <p><strong>Name:</strong> {comp.name}</p>
                          <p><strong>Category:</strong> {comp.category}</p>
                          <p><strong>Quantity:</strong> {comp.quantity}</p>
                          <p><strong>Container:</strong> {comp.container_code}</p>
                          <p><strong>Location:</strong> {locationDisplay}</p>
                          {comp.remarks && (
                            <p><strong>Remarks:</strong> {comp.remarks}</p>
                          )}
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2">
                            Component Image (Optional)
                          </label>
                          {imagePreview ? (
                            <div className="space-y-2">
                              <img
                                src={imagePreview}
                                alt="Preview"
                                className="w-32 h-32 object-cover rounded border border-zinc-600"
                              />
                              <button
                                onClick={() => handleRemoveImage(idx)}
                                className="text-xs text-red-400 hover:text-red-300"
                              >
                                Remove Image
                              </button>
                            </div>
                          ) : (
                            <input
                              type="file"
                              accept="image/*"
                              onChange={(e) => {
                                const file = e.target.files[0];
                                if (file) {
                                  handleImageChange(idx, file);
                                }
                              }}
                              className="block w-full text-sm text-zinc-300 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-zinc-700 file:text-white hover:file:bg-zinc-600"
                            />
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              <button
                onClick={handleSubmit}
                disabled={loading}
                className="mt-6 px-6 py-3 bg-green-600 hover:bg-green-700 rounded text-white font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Importing...' : `Import ${validatedComponents.length} Component(s)`}
              </button>
            </div>
          )}

          {/* Message */}
          {message && (
            <div className={`p-4 rounded-lg ${
              messageType === 'success'
                ? 'bg-green-600 text-white'
                : 'bg-red-600 text-white'
            }`}>
              {message}
            </div>
          )}
        </div>
      )}

      {activeTab === 'export' && (
        <div className="space-y-6">
          <div className="bg-zinc-800 p-6 rounded-lg border border-zinc-700">
            <h2 className="text-xl font-semibold mb-4">Export Components Report</h2>
            <p className="text-zinc-300 mb-4">
              Export all components from the inventory to an Excel file. The report will include:
            </p>
            <ul className="list-disc list-inside space-y-2 text-zinc-300 mb-6">
              <li>Component Name</li>
              <li>Category</li>
              <li>Container and Location</li>
              <li>Total Quantity</li>
              <li>Borrowed Quantity</li>
              <li>Date Added</li>
            </ul>
            <button
              onClick={handleExport}
              disabled={loading}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded text-white font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Exporting...' : 'Export Components Report'}
            </button>
          </div>

          {message && (
            <div className={`p-4 rounded-lg ${
              messageType === 'success'
                ? 'bg-green-600 text-white'
                : 'bg-red-600 text-white'
            }`}>
              {message}
            </div>
          )}
        </div>
      )}

      {activeTab === 'database' && (
        <DatabaseManagementTab
          loading={loading}
          setLoading={setLoading}
          message={message}
          setMessage={setMessage}
          messageType={messageType}
          setMessageType={setMessageType}
        />
      )}
    </div>
  );
}

function DatabaseManagementTab({ loading, setLoading, message, setMessage, messageType, setMessageType }) {
  const [previewData, setPreviewData] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [excelFile, setExcelFile] = useState(null);

  // Handle full database export
  const handleExportFull = async () => {
    setLoading(true);
    setMessage('');
    setMessageType('');

    try {
      await exportFullDatabase();
      setMessage('Full database exported successfully!');
      setMessageType('success');
    } catch (error) {
      setMessage(error.message || 'Error exporting database');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  // Handle preview restructure
  const handlePreviewRestructure = async () => {
    setLoading(true);
    setMessage('');
    setMessageType('');

    try {
      const data = await previewRestructure();
      setPreviewData(data);
      setShowPreview(true);
      setMessage('Preview loaded successfully');
      setMessageType('success');
    } catch (error) {
      setMessage(error.message || 'Error loading preview');
      setMessageType('error');
      setShowPreview(false);
    } finally {
      setLoading(false);
    }
  };

  // Handle automatic restructure
  const handleRestructure = async () => {
    if (!window.confirm(
      '⚠️ WARNING: This will permanently delete all deleted components and reorder IDs. ' +
      'A backup will be created automatically. Continue?'
    )) {
      return;
    }

    setLoading(true);
    setMessage('');
    setMessageType('');

    try {
      const result = await restructureDatabase();
      setMessage(
        `Database restructured successfully! ` +
        `${result.active_components_restructured || 0} components restructured, ` +
        `${result.deleted_components_removed || 0} deleted components removed. ` +
        `Backup saved at: ${result.backup_path || 'N/A'}`
      );
      setMessageType('success');
      setPreviewData(null);
      setShowPreview(false);
    } catch (error) {
      setMessage(error.message || 'Error restructuring database');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  // Handle Excel file selection
  const handleExcelFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.name.endsWith('.xlsx')) {
        setMessage('Please select an Excel (.xlsx) file');
        setMessageType('error');
        return;
      }
      setExcelFile(file);
      setMessage('');
    }
  };

  // Handle restructure from Excel
  const handleRestructureFromExcel = async () => {
    if (!excelFile) {
      setMessage('Please select an Excel file first');
      setMessageType('error');
      return;
    }

    if (!window.confirm(
      '⚠️ WARNING: This is a DESTRUCTIVE operation!\n\n' +
      'This will:\n' +
      '- Remove all components marked as deleted\n' +
      '- Remove borrow items referencing deleted components\n' +
      '- Replace the entire database with data from Excel\n\n' +
      'A backup will be created automatically. Continue?'
    )) {
      return;
    }

    setLoading(true);
    setMessage('');
    setMessageType('');

    try {
      const result = await restructureFromExcel(excelFile);
      setMessage(
        `Database restructured successfully from Excel! ` +
        `${result.active_components_imported || 0} components imported, ` +
        `${result.deleted_components_removed || 0} deleted components removed, ` +
        `${result.borrow_items_imported || 0} borrow items imported. ` +
        `Backup saved at: ${result.backup_path || 'N/A'}`
      );
      setMessageType('success');
      setExcelFile(null);
      // Reset file input
      const fileInput = document.getElementById('excel-restructure-input');
      if (fileInput) fileInput.value = '';
    } catch (error) {
      let errorMessage = error.message || 'Error restructuring from Excel';
      // Handle error response structure
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'object' && error.response.data.detail.errors) {
          errorMessage = `Validation errors:\n${error.response.data.detail.errors.slice(0, 5).join('\n')}`;
          if (error.response.data.detail.errors.length > 5) {
            errorMessage += `\n... and ${error.response.data.detail.errors.length - 5} more errors`;
          }
        } else {
          errorMessage = error.response.data.detail;
        }
      }
      setMessage(errorMessage);
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Export Full Database */}
      <div className="bg-zinc-800 p-6 rounded-lg border border-zinc-700">
        <h2 className="text-xl font-semibold mb-4">Export Full Database</h2>
        <p className="text-zinc-300 mb-4">
          Export the entire database to an Excel file for visualization and backup. 
          Includes all components (active and deleted), containers, borrow items, and transactions.
        </p>
        <button
          onClick={handleExportFull}
          disabled={loading}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded text-white font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Exporting...' : 'Export Full Database'}
        </button>
      </div>

      {/* Automatic Restructure */}
      <div className="bg-zinc-800 p-6 rounded-lg border border-zinc-700">
        <h2 className="text-xl font-semibold mb-4">Automatic Database Restructure</h2>
        <p className="text-zinc-300 mb-4">
          Automatically restructure the database by:
        </p>
        <ul className="list-disc list-inside space-y-2 text-zinc-300 mb-4">
          <li>Removing all deleted components</li>
          <li>Reordering component IDs sequentially (1, 2, 3...)</li>
          <li>Updating all foreign key references</li>
          <li>Preserving all borrow relationships</li>
        </ul>
        <div className="flex space-x-4">
          <button
            onClick={handlePreviewRestructure}
            disabled={loading}
            className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 rounded text-white font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Loading...' : 'Preview Changes'}
          </button>
          <button
            onClick={handleRestructure}
            disabled={loading}
            className="px-6 py-2 bg-green-600 hover:bg-green-700 rounded text-white font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Restructuring...' : 'Restructure Database'}
          </button>
        </div>
      </div>

      {/* Preview Results */}
      {showPreview && previewData && (
        <div className="bg-zinc-800 p-6 rounded-lg border border-zinc-700">
          <h3 className="text-lg font-semibold mb-4">Restructure Preview</h3>
          <div className="space-y-2 text-zinc-300">
            <p><strong>Total Active Components:</strong> {previewData.total_active_components}</p>
            <p><strong>Components to Delete:</strong> {previewData.components_to_delete}</p>
            <p><strong>ID Changes Required:</strong> {previewData.id_changes_required}</p>
            {previewData.id_mapping_preview && previewData.id_mapping_preview.length > 0 && (
              <div className="mt-4">
                <p className="font-semibold mb-2">Sample ID Mappings (first 10):</p>
                <div className="bg-zinc-900 p-4 rounded border border-zinc-600 max-h-60 overflow-y-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-zinc-600">
                        <th className="text-left p-2">Old ID</th>
                        <th className="text-left p-2">New ID</th>
                        <th className="text-left p-2">Component Name</th>
                        <th className="text-left p-2">Affected Borrow Items</th>
                      </tr>
                    </thead>
                    <tbody>
                      {previewData.id_mapping_preview.slice(0, 10).map((item, idx) => (
                        <tr key={idx} className="border-b border-zinc-700">
                          <td className="p-2">{item.old_id}</td>
                          <td className="p-2">{item.new_id}</td>
                          <td className="p-2">{item.component_name}</td>
                          <td className="p-2">{item.affected_borrow_items}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
            <p className="text-yellow-400 text-sm mt-4 italic">{previewData.note}</p>
          </div>
        </div>
      )}

      {/* Restructure from Excel */}
      <div className="bg-zinc-800 p-6 rounded-lg border border-zinc-700">
        <h2 className="text-xl font-semibold mb-4">Restructure from Excel Upload</h2>
        <div className="bg-red-900/30 border border-red-600 p-4 rounded mb-4">
          <h3 className="font-semibold text-red-400 mb-2">⚠️ DESTRUCTIVE OPERATION</h3>
          <p className="text-red-300 text-sm">
            This will completely replace the database with data from the uploaded Excel file. 
            Only upload files that were exported using "Export Full Database". 
            A backup will be created automatically, but proceed with extreme caution.
          </p>
        </div>
        <div className="space-y-4">
          <div>
            <p className="text-zinc-300 mb-2">
              Upload an Excel file (exported from "Export Full Database") with modifications:
            </p>
            <ul className="list-disc list-inside space-y-1 text-zinc-300 text-sm mb-4">
              <li>Components marked as "Is Deleted = True" will be removed</li>
              <li>Borrow items referencing deleted components will be removed</li>
              <li>Component IDs will be kept as they appear in Excel (no reshuffling)</li>
              <li>All data must be valid and properly formatted</li>
            </ul>
            <input
              id="excel-restructure-input"
              type="file"
              accept=".xlsx"
              onChange={handleExcelFileChange}
              className="block w-full text-sm text-zinc-300 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-zinc-700 file:text-white hover:file:bg-zinc-600"
            />
            {excelFile && (
              <p className="mt-2 text-zinc-400 text-sm">Selected: {excelFile.name}</p>
            )}
          </div>
          <button
            onClick={handleRestructureFromExcel}
            disabled={!excelFile || loading}
            className="px-6 py-3 bg-red-600 hover:bg-red-700 rounded text-white font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Processing...' : 'Restructure from Excel'}
          </button>
        </div>
      </div>

      {/* Message Display */}
      {message && (
        <div className={`p-4 rounded-lg whitespace-pre-line ${
          messageType === 'success'
            ? 'bg-green-600 text-white'
            : 'bg-red-600 text-white'
        }`}>
          {message}
        </div>
      )}
    </div>
  );
}

