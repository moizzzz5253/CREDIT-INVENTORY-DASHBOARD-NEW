import api from './axios.js';
import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL ?? "http://192.168.100.37:8000";

export const downloadImportTemplate = async () => {
  try {
    const response = await api.get('/import/components/template', {
      responseType: 'blob'
    });
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'component_import_template.xlsx');
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    throw error;
  }
};

export const validateExcelImport = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    // Use axios directly so it can properly detect FormData and set Content-Type with boundary
    const response = await axios.post(`${baseURL}/import/components/validate`, formData);
    return response.data;
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.message || 'Error validating Excel file';
    throw new Error(errorMessage);
  }
};

export const finalizeComponentImport = async (components) => {
  try {
    const formData = new FormData();
    formData.append('components_json', JSON.stringify(components));
    
    // Use axios directly so it can properly detect FormData and set Content-Type with boundary
    const response = await axios.post(`${baseURL}/import/components/finalize`, formData);
    return response.data;
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.message || 'Error importing components';
    throw new Error(errorMessage);
  }
};

export const uploadComponentImage = async (componentId, imageFile) => {
  try {
    const formData = new FormData();
    formData.append('component_id', componentId);
    formData.append('image', imageFile);
    
    // Use axios directly so it can properly detect FormData and set Content-Type with boundary
    const response = await axios.post(`${baseURL}/import/components/upload-image`, formData);
    return response.data;
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.message || 'Error uploading image';
    throw new Error(errorMessage);
  }
};

export const exportComponentsReport = async () => {
  try {
    const response = await api.get('/reports/components/export', {
      responseType: 'blob'
    });
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `component_report_${new Date().toISOString().split('T')[0]}.xlsx`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    throw error;
  }
};

