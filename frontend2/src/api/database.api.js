import api from './axios.js';
import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL ?? "http://192.168.100.37:8000";

export const exportFullDatabase = async () => {
  try {
    const response = await api.get('/reports/database/export-full', {
      responseType: 'blob'
    });
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `database_export_${new Date().toISOString().split('T')[0]}.xlsx`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    throw error;
  }
};

export const restructureDatabase = async () => {
  try {
    const response = await api.post('/database/restructure');
    return response.data;
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.message || 'Error restructuring database';
    throw new Error(errorMessage);
  }
};

export const previewRestructure = async () => {
  try {
    const response = await api.get('/database/restructure/preview');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const restructureFromExcel = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    // Use axios directly (without default headers) so it can properly detect FormData
    // and set Content-Type with boundary automatically
    const response = await axios.post(`${baseURL}/database/restructure/upload-excel`, formData);
    return response.data;
  } catch (error) {
    // Handle network errors
    if (!error.response) {
      const errorMsg = error.message || 'Network error';
      if (errorMsg.includes('CORS') || errorMsg.includes('Failed to fetch')) {
        throw new Error('Network error: Unable to connect to server. Please check if the backend is running and CORS is configured correctly.');
      }
      throw new Error(`Network error: ${errorMsg}`);
    }
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'Error restructuring from Excel';
    throw new Error(errorMessage);
  }
};

