import axios from "axios";
// #region agent log
fetch('http://127.0.0.1:7242/ingest/d55c5050-20f8-400e-ab29-1c5521b877bb',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'axios.js:2',message:'Axios import successful',data:{axiosType:typeof axios,hasAxios:!!axios},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
// #endregion

const baseURL = import.meta.env.VITE_API_URL ?? "http://192.168.100.37:8000";
// #region agent log
fetch('http://127.0.0.1:7242/ingest/d55c5050-20f8-400e-ab29-1c5521b877bb',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'axios.js:8',message:'API baseURL configured',data:{baseURL,hasEnv:!!import.meta.env.VITE_API_URL},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
// #endregion

const api = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});
// #region agent log
fetch('http://127.0.0.1:7242/ingest/d55c5050-20f8-400e-ab29-1c5521b877bb',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'axios.js:15',message:'Axios instance created',data:{hasApi:!!api},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
// #endregion

export default api;
