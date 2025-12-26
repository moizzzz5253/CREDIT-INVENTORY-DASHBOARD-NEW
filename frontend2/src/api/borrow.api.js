import api from './axios.js';
// #region agent log
fetch('http://127.0.0.1:7242/ingest/d55c5050-20f8-400e-ab29-1c5521b877bb',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'borrow.api.js:1',message:'borrow.api api import attempt',data:{importPath:'./axios.js',hasApi:!!api},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
// #endregion

export const createBorrow = async (borrowData) => {
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/d55c5050-20f8-400e-ab29-1c5521b877bb',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'borrow.api.js:5',message:'createBorrow called',data:{usingApiInstance:true},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
  // #endregion
  try {
    const response = await api.post('/borrow', borrowData);
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/d55c5050-20f8-400e-ab29-1c5521b877bb',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'borrow.api.js:11',message:'createBorrow success',data:{status:response.status},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    return response.data;
  } catch (error) {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/d55c5050-20f8-400e-ab29-1c5521b877bb',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'borrow.api.js:14',message:'createBorrow error',data:{error:error.message,status:error.response?.status},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    throw error;
  }
};

export const getActiveBorrows = async () => {
  try {
    const response = await api.get('/borrow/active');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getBorrowDetails = async (borrowId) => {
  try {
    const response = await api.get(`/borrow/${borrowId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};