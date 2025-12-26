import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getActiveBorrows } from '../api/borrow.api.js';
import { returnComponent } from '../api/returns.api.js';

export default function BorrowActive() {
  const [borrowGroups, setBorrowGroups] = useState([]);
  const [filteredBorrowGroups, setFilteredBorrowGroups] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedCards, setExpandedCards] = useState(new Set());
  const [returnModal, setReturnModal] = useState(null); // { item, borrower }
  const [returnForm, setReturnForm] = useState({
    quantity: '',
    returnAll: false,
    pic_name: '',
    remarks: ''
  });
  const [returnLoading, setReturnLoading] = useState(false);
  const [returnMessage, setReturnMessage] = useState('');
  const [returnMessageType, setReturnMessageType] = useState(''); // 'success' or 'error'
  const navigate = useNavigate();

  // Function to fetch and process borrows
  const fetchAndProcessBorrows = async () => {
    try {
      const data = await getActiveBorrows();
      
      // Group borrows by tp_id (user)
      const groupedByUser = {};
      
      data.forEach(item => {
        const userId = item.tp_id;
        
        // Initialize user group if it doesn't exist
        if (!groupedByUser[userId]) {
          groupedByUser[userId] = {
            borrower: {
              name: item.borrower_name,
              tp_id: item.tp_id,
              phone: item.phone
            },
            items: [],
            hasOverdue: false
          };
        }
        
        // Add item to user's borrow list
        const borrowItem = {
          transaction_id: item.transaction_id,
          component_id: item.component_id,
          component_name: item.component_name,
          remaining_quantity: item.remaining_quantity,
          quantity_borrowed: item.quantity_borrowed || item.remaining_quantity,
          expected_return_date: item.expected_return_date,
          borrowed_by_pic: item.borrowed_by_pic,
          status: item.status,
          is_overdue: item.is_overdue || false,
          days_overdue: item.days_overdue || 0
        };
        
        groupedByUser[userId].items.push(borrowItem);
        
        // Check if this item is overdue
        if (item.is_overdue || item.status === 'OVERDUE') {
          groupedByUser[userId].hasOverdue = true;
        }
      });
      
      // Convert grouped object to array and sort by borrower name
      const groupedArray = Object.values(groupedByUser).sort((a, b) => 
        a.borrower.name.localeCompare(b.borrower.name)
      );
      
      setBorrowGroups(groupedArray);
      setFilteredBorrowGroups(groupedArray);
    } catch (error) {
      console.error('Error fetching active borrows:', error);
    }
  };

  // Fetch and group borrows by user
  useEffect(() => {
    fetchAndProcessBorrows();
  }, []);

  // Filter borrow groups based on search term
  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredBorrowGroups(borrowGroups);
      return;
    }

    const searchLower = searchTerm.toLowerCase();
    const filtered = borrowGroups.filter(group => 
      group.borrower.name.toLowerCase().includes(searchLower) ||
      group.borrower.tp_id.toLowerCase().includes(searchLower) ||
      group.borrower.phone.toLowerCase().includes(searchLower) ||
      group.items.some(item => 
        item.component_name.toLowerCase().includes(searchLower)
      )
    );
    
    setFilteredBorrowGroups(filtered);
  }, [searchTerm, borrowGroups]);

  // Toggle card expansion
  const toggleCard = (tpId) => {
    setExpandedCards(prev => {
      const next = new Set(prev);
      if (next.has(tpId)) {
        next.delete(tpId);
      } else {
        next.add(tpId);
      }
      return next;
    });
  };

  // Open return modal
  const handleReturnClick = (item, borrower) => {
    setReturnModal({ item, borrower });
    setReturnForm({
      quantity: '',
      returnAll: false,
      pic_name: '',
      remarks: ''
    });
    setReturnMessage('');
    setReturnMessageType('');
  };

  // Close return modal
  const handleCloseReturnModal = () => {
    setReturnModal(null);
    setReturnForm({
      quantity: '',
      returnAll: false,
      pic_name: '',
      remarks: ''
    });
    setReturnMessage('');
    setReturnMessageType('');
  };

  // Handle return form change
  const handleReturnFormChange = (field, value) => {
    if (field === 'returnAll') {
      setReturnForm(prev => ({
        ...prev,
        returnAll: value,
        quantity: value ? returnModal.item.remaining_quantity : ''
      }));
    } else {
      setReturnForm(prev => ({ ...prev, [field]: value }));
    }
  };

  // Handle return submit
  const handleReturnSubmit = async (e) => {
    e.preventDefault();
    if (!returnModal) return;

    // Validation
    if (!returnForm.pic_name.trim()) {
      setReturnMessage('PIC name is required');
      setReturnMessageType('error');
      return;
    }

    const quantityToReturn = returnForm.returnAll 
      ? returnModal.item.remaining_quantity 
      : parseInt(returnForm.quantity);

    if (!quantityToReturn || quantityToReturn <= 0) {
      setReturnMessage('Please enter a valid quantity to return');
      setReturnMessageType('error');
      return;
    }

    if (quantityToReturn > returnModal.item.remaining_quantity) {
      setReturnMessage(`Return quantity (${quantityToReturn}) exceeds remaining borrowed quantity (${returnModal.item.remaining_quantity})`);
      setReturnMessageType('error');
      return;
    }

    setReturnLoading(true);
    setReturnMessage('');
    setReturnMessageType('');

    try {
      await returnComponent({
        transaction_id: returnModal.item.transaction_id,
        component_id: returnModal.item.component_id,
        quantity: quantityToReturn,
        pic_name: returnForm.pic_name.trim(),
        remarks: returnForm.remarks.trim() || null
      });

      setReturnMessage('Return successful!');
      setReturnMessageType('success');

      // Refresh borrows list
      await fetchAndProcessBorrows();

      // Close modal after delay
      setTimeout(() => {
        handleCloseReturnModal();
      }, 2000);
    } catch (error) {
      setReturnMessage(error.message || 'An error occurred while processing the return');
      setReturnMessageType('error');
    } finally {
      setReturnLoading(false);
    }
  };

  return (
    <div className="p-6 bg-zinc-900 text-zinc-200 min-h-screen">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Active Borrows</h1>
        <button
          onClick={() => navigate('/borrow/new')}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white transition-colors"
        >
          New Borrow
        </button>
      </div>

      <input
        type="text"
        placeholder="Search by name, TP ID, phone, or component"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="w-full p-2 bg-zinc-700 border border-zinc-600 rounded mb-4 text-white placeholder-zinc-400 focus:outline-none focus:border-blue-500"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredBorrowGroups.map((group) => {
          const tpId = group.borrower.tp_id;
          const isExpanded = expandedCards.has(tpId);
          
          return (
            <div
              key={tpId}
              className={`rounded-xl p-4 border-2 transition-all duration-200 ${
                group.hasOverdue
                  ? 'bg-red-900/50 border-red-600'
                  : 'bg-zinc-800 border-zinc-700'
              }`}
            >
              {/* Card Header - Clickable */}
              <div
                className="flex justify-between items-start cursor-pointer"
                onClick={() => toggleCard(tpId)}
              >
                <div className="flex-1">
                  <h3 className="font-semibold text-white text-lg mb-1">
                    {group.borrower.name}
                  </h3>
                  <p className="text-zinc-300 text-sm">TP ID: {group.borrower.tp_id}</p>
                  <p className="text-zinc-300 text-sm">Phone: {group.borrower.phone}</p>
                </div>

                {/* Expand/Collapse Icon */}
                <span
                  className={`text-white text-xl ml-2 transition-transform duration-200 ${
                    isExpanded ? 'rotate-180' : ''
                  }`}
                >
                  ▼
                </span>
              </div>

              {/* Expanded Content */}
              {isExpanded && (
                <div className="mt-4 pt-4 border-t border-zinc-600 space-y-3">
                  {group.items.length > 0 ? (
                    group.items.map((item, index) => {
                      const isItemOverdue = item.is_overdue || item.status === 'OVERDUE';
                      
                      return (
                        <div
                          key={index}
                          className={`bg-zinc-900 p-3 rounded-lg border ${
                            isItemOverdue
                              ? 'border-red-500 border-2'
                              : 'border-zinc-700'
                          }`}
                        >
                          {/* Prominent Overdue Badge */}
                          {isItemOverdue && (
                            <div className="mb-2 px-3 py-1 bg-red-600 text-white text-xs font-bold rounded inline-block">
                              ⚠ OVERDUE {item.days_overdue > 0 ? `(${item.days_overdue} day${item.days_overdue > 1 ? 's' : ''} overdue)` : ''}
                            </div>
                          )}
                          
                          <p className="text-white mb-2">
                            <strong>Component:</strong> {item.component_name}
                          </p>
                          <p className="text-zinc-300 text-sm mb-1">
                            <strong>Quantity:</strong> {item.remaining_quantity}
                          </p>
                          <p className="text-zinc-300 text-sm mb-1">
                            <strong>Expected Return:</strong>{' '}
                            <span className={`text-base font-medium ${
                              isItemOverdue ? 'text-red-400' : ''
                            }`}>
                              {item.expected_return_date 
                                ? new Date(item.expected_return_date).toLocaleDateString('en-US', {
                                    year: 'numeric',
                                    month: 'short',
                                    day: 'numeric'
                                  })
                                : 'N/A'}
                            </span>
                          </p>
                          <p className="text-zinc-300 text-sm mb-1">
                            <strong>PIC:</strong> {item.borrowed_by_pic}
                          </p>
                          {!isItemOverdue && (
                            <p className="text-sm mb-3">
                              <span className="text-green-400 font-semibold">
                                {item.status}
                              </span>
                            </p>
                          )}
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleReturnClick(item, group.borrower);
                            }}
                            className="w-full px-3 py-2 bg-green-600 hover:bg-green-700 rounded text-white text-sm font-medium transition-colors"
                          >
                            Return
                          </button>
                        </div>
                      );
                    })
                  ) : (
                    <div className="bg-zinc-900 p-3 rounded-lg border border-zinc-700 text-zinc-400 text-center">
                      No borrowed items
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Return Modal */}
      {returnModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={handleCloseReturnModal}>
          <div className="bg-zinc-800 rounded-lg p-6 w-full max-w-md mx-4 border border-zinc-700" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-2xl font-bold text-white mb-4">Return Component</h2>
            
            {/* Borrower Info */}
            <div className="bg-zinc-900 p-3 rounded mb-4 border border-zinc-700">
              <p className="text-white mb-1">
                <strong>Borrower Name:</strong> {returnModal.borrower.name}
              </p>
              <p className="text-zinc-300 text-sm">
                <strong>TP ID:</strong> {returnModal.borrower.tp_id}
              </p>
            </div>

            {/* Component Info */}
            <div className="bg-zinc-900 p-3 rounded mb-4 border border-zinc-700">
              <p className="text-white mb-1">
                <strong>Component:</strong> {returnModal.item.component_name}
              </p>
              <p className="text-zinc-300 text-sm">
                <strong>Quantity Borrowed:</strong> {returnModal.item.remaining_quantity}
              </p>
            </div>

            <form onSubmit={handleReturnSubmit} className="space-y-4">
              {/* Return All Option */}
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="returnAll"
                  checked={returnForm.returnAll}
                  onChange={(e) => handleReturnFormChange('returnAll', e.target.checked)}
                  className="w-4 h-4 text-green-600 bg-zinc-700 border-zinc-600 rounded focus:ring-green-500"
                />
                <label htmlFor="returnAll" className="text-white cursor-pointer">
                  Return all quantity ({returnModal.item.remaining_quantity})
                </label>
              </div>

              {/* Quantity Input */}
              {!returnForm.returnAll && (
                <div>
                  <label className="block text-zinc-300 mb-1">Quantity to Return</label>
                  <input
                    type="number"
                    min="1"
                    max={returnModal.item.remaining_quantity}
                    value={returnForm.quantity}
                    onChange={(e) => handleReturnFormChange('quantity', e.target.value)}
                    className="w-full p-2 bg-zinc-700 border border-zinc-600 rounded text-white"
                    required={!returnForm.returnAll}
                    disabled={returnForm.returnAll}
                  />
                  <p className="text-zinc-400 text-xs mt-1">
                    Maximum: {returnModal.item.remaining_quantity}
                  </p>
                </div>
              )}

              {/* PIC Name */}
              <div>
                <label className="block text-zinc-300 mb-1">PIC Name <span className="text-red-400">*</span></label>
                <input
                  type="text"
                  value={returnForm.pic_name}
                  onChange={(e) => handleReturnFormChange('pic_name', e.target.value)}
                  className="w-full p-2 bg-zinc-700 border border-zinc-600 rounded text-white"
                  required
                  placeholder="Enter PIC name"
                />
              </div>

              {/* Remarks */}
              <div>
                <label className="block text-zinc-300 mb-1">Remarks (Optional)</label>
                <textarea
                  value={returnForm.remarks}
                  onChange={(e) => handleReturnFormChange('remarks', e.target.value)}
                  className="w-full p-2 bg-zinc-700 border border-zinc-600 rounded text-white"
                  rows="3"
                  placeholder="Enter any remarks..."
                />
              </div>

              {/* Error/Success Message */}
              {returnMessage && (
                <div className={`p-3 rounded ${
                  returnMessageType === 'success' 
                    ? 'bg-green-600 text-white' 
                    : 'bg-red-600 text-white'
                }`}>
                  {returnMessage}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={handleCloseReturnModal}
                  className="flex-1 px-4 py-2 bg-zinc-700 hover:bg-zinc-600 rounded text-white transition-colors"
                  disabled={returnLoading}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={returnLoading}
                  className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-white transition-colors disabled:opacity-50"
                >
                  {returnLoading ? 'Processing...' : 'Confirm Return'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
