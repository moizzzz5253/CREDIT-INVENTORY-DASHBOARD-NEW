
import { useNavigate } from "react-router-dom";

export default function ContainerCard({ container }) {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate(`/containers/${container.code}`)}
      className="cursor-pointer bg-zinc-800 border border-zinc-700 rounded-lg p-4
                 hover:scale-[1.02] hover:border-blue-500 transition"
    >
      <div className="text-sm text-zinc-400">
        Cabinet {container.cabinet_number}
      </div>

      <div className="text-lg font-semibold mb-2">
        {container.code}
      </div>

      <img
        src={`${import.meta.env.VITE_API_BASE_URL}${container.qr_path}`}
        alt={container.code}
        className="w-full rounded-md bg-white p-2"
      />
    </div>
  );
}
