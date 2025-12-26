import api from './axios.js';

export const getReturnHistory = async () => {
  try {
    const response = await api.get('/history/');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getDeletedComponentsHistory = async () => {
  try {
    const response = await api.get('/history/deleted-components/');
    return response.data;
  } catch (error) {
    throw error;
  }
};

