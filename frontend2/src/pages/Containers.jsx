import React, { useEffect, useState } from "react";
import {
  getAllContainers,
  initContainers,
  regenerateQRCodes,
} from "../api/containers.api";
import { useNavigate } from "react-router-dom";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000"; // backend base
// #region agent log
fetch('http://127.0.0.1:7242/ingest/d55c5050-20f8-400e-ab29-1c5521b877bb',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Containers.jsx:10',message:'API_BASE defined in Containers',data:{API_BASE,hasEnv:!!import.meta.env.VITE_API_URL},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
// #endregion



export default function Containers() {
  const [containers, setContainers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");
  const [qrVersion, setQrVersion] = useState(0);
  const navigate = useNavigate();

  const loadContainers = async () => {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/d55c5050-20f8-400e-ab29-1c5521b877bb',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Containers.jsx:20',message:'loadContainers called',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
    // #endregion
    setLoading(true);
    try {
      const data = await getAllContainers();
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/d55c5050-20f8-400e-ab29-1c5521b877bb',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Containers.jsx:24',message:'getAllContainers success',data:{hasData:!!data,dataLength:Array.isArray(data)?data.length:'not-array'},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
      // #endregion
      setContainers(data);
    } catch (error) {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/d55c5050-20f8-400e-ab29-1c5521b877bb',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Containers.jsx:27',message:'getAllContainers error',data:{error:error.message,stack:error.stack},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'B'})}).catch(()=>{});
      // #endregion
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadContainers();
  }, []);

  useEffect(() => {
  console.log("Containers API response:", containers);
  
}, [containers]);


  const handleInit = async () => {
    await initContainers();
    loadContainers();
  };

  const handleRegenerateQR = async () => {
    await regenerateQRCodes();
    setQrVersion(Date.now()); // Force QR code image reload
    loadContainers();
  };

  const filteredContainers = containers.filter(c => 
    c.code.toLowerCase().includes(search.toLowerCase())
  );

  const handlePrint = () => {
    const printWindow = window.open('', '_blank');
    const cacheBust = qrVersion || Date.now();
    const labelsHtml = filteredContainers.map(c => `
      <div style="width:8cm; height:8cm; border:1px solid black; display:flex; flex-direction:column; align-items:center; justify-content:center; margin:0.5cm; box-sizing:border-box; page-break-inside:avoid;">
        <img src="${API_BASE}/${c.qr_path}?v=${cacheBust}" style="width:6cm; height:6cm; object-fit:contain;" />
        <div style="font-size:45; font-weight:bold; margin-top:0.5cm;">${c.code}</div>
      </div>
    `).join('');
    const fullHtml = `<html><head><title>QR Labels</title><style>@media print { body { margin:0; } }</style></head><body style="display:flex; flex-wrap:wrap; justify-content:flex-start;">${labelsHtml}</body></html>`;
    printWindow.document.write(fullHtml);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
      printWindow.print();
      printWindow.close();
    }, 1000);
  };

  // #region agent log
  useEffect(() => {
    fetch('http://127.0.0.1:7242/ingest/d55c5050-20f8-400e-ab29-1c5521b877bb',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Containers.jsx:85',message:'Containers rendering',data:{containersCount:containers.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
  }, [containers.length]);
  // #endregion
  return (
    <>
      {/* Top controls */}
      <div className="flex flex-wrap gap-3 mb-6">
        <input
          type="text"
          placeholder="Search container..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="px-3 py-2 rounded bg-zinc-800 border border-zinc-700"
        />

        <button
          onClick={handleInit}
          className="px-4 py-2 bg-blue-600 rounded"
        >
          Init Containers
        </button>

        <button
          onClick={handleRegenerateQR}
          className="px-4 py-2 bg-orange-600 rounded"
        >
          Regenerate QR Codes
        </button>

        <button
          onClick={handlePrint}
          className="px-4 py-2 bg-green-600 rounded"
        >
          Print QR Labels
        </button>
      </div>

      {/* Container grid */}
      {loading ? (
        <div>Loading containers…</div>
      ) : filteredContainers.length === 0 ? (
        <div className="text-center text-zinc-400 mt-10">
          {search ? "No containers match your search." : "No containers found."}
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-6">
          {filteredContainers.map((c) => (
            <div
              key={c.id}
              onClick={() => navigate(`/containers/${c.code}`)}
              className="bg-zinc-900 border border-zinc-700 rounded-lg p-3 flex flex-col items-center cursor-pointer hover:border-blue-500 transition"
            >
              <img
                src={`${API_BASE}/${c.qr_path}${qrVersion ? `?v=${qrVersion}` : ''}`}
                alt={`QR ${c.code}`}
                className="w-32 h-32 object-contain bg-white p-1 rounded"
                onError={(e) => {
                  e.currentTarget.src = "/placeholder.png";
                }}
                key={`${c.code}-${qrVersion}`}
              />

              <div className="mt-2 font-semibold text-lg">{c.code}</div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
