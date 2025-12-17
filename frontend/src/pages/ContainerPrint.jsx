import { useEffect, useState } from "react";
import { getAllContainers } from "../api/containers.api";

export default function ContainerPrint() {
  const [containers, setContainers] = useState([]);

  useEffect(() => {
    getAllContainers().then(setContainers);
  }, []);

  return (
    <div className="print-page">
      <div className="print-toolbar">
        <button onClick={() => window.print()}>
          Print QR Codes
        </button>
      </div>

      <div className="qr-grid">
        {containers.map((c) => (
          <div key={c.id} className="qr-card">
            <img
              src={`${import.meta.env.VITE_API_BASE_URL}${c.qr_path}`}
              alt={c.code}
            />
            <div className="qr-label">{c.code}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
