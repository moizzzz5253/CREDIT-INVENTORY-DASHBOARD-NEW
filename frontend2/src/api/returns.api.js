import api from './axios.js';

export const returnComponent = async (returnData) => {
  try {
    // Build query parameters
    const params = new URLSearchParams({
      transaction_id: returnData.transaction_id.toString(),
      component_id: returnData.component_id.toString(),
      quantity: returnData.quantity.toString(),
      pic_name: returnData.pic_name
    });
    
    // Add remarks only if provided
    if (returnData.remarks) {
      params.append('remarks', returnData.remarks);
    }

    const response = await api.post(`/returns/?${params.toString()}`);
    return response.data;
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'An error occurred while processing the return';
    throw new Error(errorMessage);
  }
};

export const returnComponentsBatch = async (batchData) => {
  try {
    const response = await api.post('/returns/batch', batchData);
    return response.data;
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message || 'An error occurred while processing the batch return';
    throw new Error(errorMessage);
  }
};

