export default function ActiveBorrowCard({ data }) {
  return (
    <div className="border border-zinc-700 rounded-lg p-4">
      <h4 className="font-semibold">{data.borrower_name}</h4>
      <p className="text-sm">{data.tp_id}</p>
      <p className="text-sm">{data.phone}</p>

      <div className="mt-2">
        <span className="font-medium">{data.component}</span> ×{" "}
        {data.quantity}
      </div>

      <div className="text-sm mt-1">
        Return: {data.expected_return_date}
      </div>

      <span
        className={`inline-block mt-2 px-2 py-1 rounded text-xs ${
          data.status === "OVERDUE"
            ? "bg-red-600"
            : "bg-green-600"
        }`}
      >
        {data.status}
      </span>
    </div>
  );
}
