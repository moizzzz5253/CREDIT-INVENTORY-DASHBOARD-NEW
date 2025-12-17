import { useEffect, useState } from "react";
import { createBorrow } from "../../api/borrow.api";
import { getAllComponents } from "../../api/components.api";
import BorrowItemRow from "./BorrowItemRow";

export default function BorrowForm({ onSuccess }) {
  const [components, setComponents] = useState([]);
  const [items, setItems] = useState([{ component_id: "", quantity: 1 }]);

  const [borrower, setBorrower] = useState({
    name: "",
    tp_id: "",
    countryCode: "+60",
    phone: "",
  });

  const [reason, setReason] = useState("");
  const [returnDate, setReturnDate] = useState("");

  useEffect(() => {
    getAllComponents().then(setComponents);
  }, []);

  const submit = async (e) => {
    e.preventDefault();

    const payload = {
      borrower: {
        name: borrower.name,
        tp_id: borrower.tp_id,
        phone: borrower.countryCode.replace("+", "") + borrower.phone,
      },
      reason,
      expected_return_date: returnDate,
      items,
    };

    await createBorrow(payload);
    onSuccess();
  };
  const COUNTRY_CODES = [
  { label: "Malaysia (+60)", value: "+60" },
  { label: "Singapore (+65)", value: "+65" },
  { label: "Indonesia (+62)", value: "+62" },
  { label: "Thailand (+66)", value: "+66" },
  { label: "India (+91)", value: "+91" },
];


  return (
    <form onSubmit={submit} className="space-y-4 bg-zinc-900 p-6 rounded-lg">
      <h3 className="text-lg font-semibold">Borrow Components</h3>

      <input
        className="w-full bg-zinc-800 p-2 rounded"
        placeholder="Full name as per TP card"
        value={borrower.name}
        onChange={(e) =>
          setBorrower({ ...borrower, name: e.target.value })
        }
        required
      />

      <input
        className="w-full bg-zinc-800 p-2 rounded"
        placeholder="TP ID"
        value={borrower.tp_id}
        onChange={(e) =>
          setBorrower({ ...borrower, tp_id: e.target.value })
        }
        required
      />

      <div className="flex gap-2">
       <select
        className="bg-zinc-800 p-2 rounded"
        value={borrower.countryCode}
        onChange={(e) =>
            setBorrower({ ...borrower, countryCode: e.target.value })
        }
        >
            {COUNTRY_CODES.map((c) => (
                <option key={c.value} value={c.value}>
                {c.label}
            </option>
          ))}
        </select>


        <input
          className="flex-1 bg-zinc-800 p-2 rounded"
          placeholder="Phone number"
          value={borrower.phone}
          onChange={(e) =>
            setBorrower({ ...borrower, phone: e.target.value })
          }
          required
        />
      </div>

      <input
        type="date"
        className="w-full bg-zinc-800 p-2 rounded"
        value={returnDate}
        onChange={(e) => setReturnDate(e.target.value)}
        required
      />

      <textarea
        className="w-full bg-zinc-800 p-2 rounded"
        placeholder="Reason (required)"
        value={reason}
        onChange={(e) => setReason(e.target.value)}
        required
      />

      <div className="space-y-2">
        {items.map((item, idx) => (
          <BorrowItemRow
            key={idx}
            components={components}
            item={item}
            onChange={(updated) =>
              setItems(items.map((i, j) => (j === idx ? updated : i)))
            }
            onRemove={() =>
              setItems(items.filter((_, j) => j !== idx))
            }
          />
        ))}
      </div>

      <button
        type="button"
        onClick={() =>
          setItems([...items, { component_id: "", quantity: 1 }])
        }
        className="text-blue-400"
      >
        + Add another component
      </button>

      <button
        type="submit"
        className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded"
      >
        Submit Borrow
      </button>
    </form>
  );
}
