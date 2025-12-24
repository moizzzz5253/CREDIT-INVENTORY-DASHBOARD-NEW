import axios from './axios.js';

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export const createBorrow = async (borrowData) => {
  try {
    const response = await axios.post(`${API_BASE}/borrow`, borrowData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getActiveBorrows = async () => {
  try {
    const response = await axios.get(`${API_BASE}/borrow/active`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getBorrowDetails = async (borrowId) => {
  try {
    const response = await axios.get(`${API_BASE}/borrow/${borrowId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};