import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getActiveBorrows } from '../api/borrow.api.js';

export default function BorrowActive() {
  const [borrows, setBorrows] = useState([]);
  const [filteredBorrows, setFilteredBorrows] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedCards, setExpandedCards] = useState(new Set());
  const navigate = useNavigate();

  useEffect(() => {
    const fetchBorrows = async () => {
      const data = await getActiveBorrows();

      const grouped = {};
      data.forEach(item => {
        const key = item.tp_id;
        if (!grouped[key]) {
          grouped[key] = {
            borrower: {
              name: item.borrower_name,
              tp_id: item.tp_id,
              phone: item.phone
            },
            items: [],
            isOverdue: false
          };
        }

        grouped[key].items.push({
          component_name: item.component_name,
          remaining_quantity: item.remaining_quantity,
          expected_return_date: item.expected_return_date,
          borrowed_by_pic: item.borrowed_by_pic,
          status: item.status
        });

        if (item.status === 'OVERDUE') {
          grouped[key].isOverdue = true;
        }
      });

      const arr = Object.values(grouped);
      setBorrows(arr);
      setFilteredBorrows(arr);
    };

    fetchBorrows();
  }, []);

  useEffect(() => {
    if (!searchTerm) {
      setFilteredBorrows(borrows);
    } else {
      const term = searchTerm.toLowerCase();
      setFilteredBorrows(
        borrows.filter(b =>
          b.borrower.name.toLowerCase().includes(term) ||
          b.borrower.tp_id.toLowerCase().includes(term) ||
          b.items.some(i =>
            i.component_name.toLowerCase().includes(term)
          )
        )
      );
    }
  }, [searchTerm, borrows]);

  const toggleCard = (tpId) => {
    setExpandedCards(prev => {
      const next = new Set(prev);
      next.has(tpId) ? next.delete(tpId) : next.add(tpId);
      return next;
    });
  };

  return (
    <div className="p-6 bg-zinc-900 text-zinc-200 min-h-screen">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Active Borrows</h1>
        <button
          onClick={() => navigate('/borrow/new')}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white"
        >
          New Borrow
        </button>
      </div>

      <input
        type="text"
        placeholder="Search by name, ID, or component"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="w-full p-2 bg-zinc-700 border border-zinc-600 rounded mb-4"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredBorrows.map(borrow => {
          const tpId = borrow.borrower.tp_id;
          const isExpanded = expandedCards.has(tpId);

          return (
            <div
              key={tpId}
              className={`rounded-xl p-4 border transition-all duration-300 hover:shadow-lg hover:scale-105 ${
                borrow.isOverdue
                  ? 'bg-red-900 border-red-700'
                  : 'bg-green-900 border-green-700'
              }`}
            >
              {/* 🔒 CLICK ONLY HERE */}
              <div
                className="flex justify-between items-center cursor-pointer"
                onClick={() => toggleCard(tpId)}
              >
                <div>
                  <h3 className="font-semibold text-white">
                    {borrow.borrower.name}
                  </h3>
                  <p className="text-zinc-300">TP ID: {tpId}</p>
                  <p className="text-zinc-300">
                    Phone: {borrow.borrower.phone}
                  </p>
                </div>

                <span
                  className={`text-white text-xl transition-transform ${
                    isExpanded ? 'rotate-180' : ''
                  }`}
                >
                  ▼
                </span>
              </div>

              {isExpanded && (
                <div className="mt-4 space-y-2">
                  {borrow.items.map((item, idx) => (
                    <div
                      key={idx}
                      className="bg-zinc-800 p-2 rounded border border-zinc-600"
                    >
                      <p><strong>Component:</strong> {item.component_name}</p>
                      <p><strong>Qty Borrowed:</strong> {item.remaining_quantity}</p>
                      <p><strong>Expected Return:</strong> {item.expected_return_date}</p>
                      <p><strong>PIC:</strong> {item.borrowed_by_pic}</p>
                      <p><strong>Status:</strong> {item.status}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
