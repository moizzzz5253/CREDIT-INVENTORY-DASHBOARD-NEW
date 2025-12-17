import { useEffect, useState } from "react";
import DashboardLayout from "../layouts/DashboardLayout";
import BorrowForm from "../components/borrow/BorrowForm";
import ActiveBorrowCard from "../components/borrow/ActiveBorrowCard";
import { getActiveBorrowers } from "../api/borrow.api";

export default function Borrow() {
  const [active, setActive] = useState([]);
  const [mode, setMode] = useState("add");


  const refresh = () => {
    getActiveBorrowers().then(setActive);
  };

  useEffect(refresh, []);

  return (
    <DashboardLayout>
      
      <BorrowForm onSuccess={refresh} />

      <h3 className="text-lg font-semibold mt-8 mb-4">
        Active Borrowers
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {active.map((b, i) => (
          <ActiveBorrowCard key={i} data={b} />
        ))}
      </div>
    </DashboardLayout>
  );
}
