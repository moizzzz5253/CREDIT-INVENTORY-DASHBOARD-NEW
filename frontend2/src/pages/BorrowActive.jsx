import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getActiveBorrows } from '../api/borrow.api.js';
import { returnComponent, returnComponentsBatch } from '../api/returns.api.js';

export default function BorrowActive() {
  const [borrowGroups, setBorrowGroups] = useState([]);
  const [filteredBorrowGroups, setFilteredBorrowGroups] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedCards, setExpandedCards] = useState(new Set());
  const [returnModal, setReturnModal] = useState(null); // { borrower, availableItems }
  const [returnItems, setReturnItems] = useState([]); // Array of { item, quantity, returnAll, remarks }
  const [returnForm, setReturnForm] = useState({
    pic_name: ''
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
              phone: item.phone,
              email: item.email || ''
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
      (group.borrower.email && group.borrower.email.toLowerCase().includes(searchLower)) ||
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

  // Open return modal with initial item
  const handleReturnClick = (item, borrower) => {
    // Get all available items for this borrower
    const borrowerGroup = borrowGroups.find(g => g.borrower.tp_id === borrower.tp_id);
    const availableItems = borrowerGroup ? borrowerGroup.items.filter(i => i.remaining_quantity > 0) : [item];
    
    setReturnModal({ borrower, availableItems });
    // Initialize with the clicked item
    setReturnItems([{
      item: item,
      quantity: '',
      returnAll: false,
      remarks: ''
    }]);
    setReturnForm({
      pic_name: ''
    });
    setReturnMessage('');
    setReturnMessageType('');
  };

  // Close return modal
  const handleCloseReturnModal = () => {
    setReturnModal(null);
    setReturnItems([]);
    setReturnForm({
      pic_name: ''
    });
    setReturnMessage('');
    setReturnMessageType('');
  };
  
  // Add another item to return batch
  const handleAddReturnItem = () => {
    if (!returnModal) return;
    
    // Find first available item not already in returnItems
    const existingItemIds = new Set(returnItems.map(ri => ri.item.component_id));
    const availableItem = returnModal.availableItems.find(
      item => !existingItemIds.has(item.component_id) && item.remaining_quantity > 0
    );
    
    if (availableItem) {
      setReturnItems(prev => [...prev, {
        item: availableItem,
        quantity: '',
        returnAll: false,
        remarks: ''
      }]);
    }
  };
  
  // Remove item from return batch
  const handleRemoveReturnItem = (index) => {
    setReturnItems(prev => prev.filter((_, i) => i !== index));
  };
  
  // Update return item field
  const handleReturnItemChange = (index, field, value) => {
    setReturnItems(prev => {
      const updated = [...prev];
      if (field === 'returnAll') {
        updated[index] = {
          ...updated[index],
          returnAll: value,
          quantity: value ? updated[index].item.remaining_quantity : ''
        };
      } else {
        updated[index] = {
          ...updated[index],
          [field]: value
        };
      }
      return updated;
    });
  };

  // Handle return form change (for PIC name)
  const handleReturnFormChange = (field, value) => {
    setReturnForm(prev => ({ ...prev, [field]: value }));
  };

  // Handle batch return submit
  const handleReturnSubmit = async (e) => {
    e.preventDefault();
    if (!returnModal || returnItems.length === 0) return;

    // Validation
    if (!returnForm.pic_name.trim()) {
      setReturnMessage('PIC name is required');
      setReturnMessageType('error');
      return;
    }

    // Validate all items
    const batchItems = [];
    for (let i = 0; i < returnItems.length; i++) {
      const returnItem = returnItems[i];
      const quantityToReturn = returnItem.returnAll 
        ? returnItem.item.remaining_quantity 
        : parseInt(returnItem.quantity);

      if (!quantityToReturn || quantityToReturn <= 0) {
        setReturnMessage(`Please enter a valid quantity for ${returnItem.item.component_name}`);
        setReturnMessageType('error');
        return;
      }

      if (quantityToReturn > returnItem.item.remaining_quantity) {
        setReturnMessage(`Return quantity (${quantityToReturn}) exceeds remaining borrowed quantity (${returnItem.item.remaining_quantity}) for ${returnItem.item.component_name}`);
        setReturnMessageType('error');
        return;
      }

      batchItems.push({
        transaction_id: returnItem.item.transaction_id,
        component_id: returnItem.item.component_id,
        quantity: quantityToReturn,
        remarks: returnItem.remarks.trim() || null
      });
    }

    setReturnLoading(true);
    setReturnMessage('');
    setReturnMessageType('');

    try {
      await returnComponentsBatch({
        pic_name: returnForm.pic_name.trim(),
        items: batchItems
      });

      setReturnMessage(`Successfully returned ${batchItems.length} item(s)!`);
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
        placeholder="Search by name, TP ID, phone, email, or component"
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
                  {group.borrower.email && (
                    <p className="text-zinc-300 text-sm">Email: {group.borrower.email}</p>
                  )}
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
          <div className="bg-zinc-800 rounded-lg p-6 w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto border border-zinc-700" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-2xl font-bold text-white mb-4">Return Items</h2>
            
            {/* Borrower Info */}
            <div className="bg-zinc-900 p-3 rounded mb-4 border border-zinc-700">
              <p className="text-white mb-1">
                <strong>Borrower Name:</strong> {returnModal.borrower.name}
              </p>
              <p className="text-zinc-300 text-sm">
                <strong>TP ID:</strong> {returnModal.borrower.tp_id}
              </p>
              {returnModal.borrower.email && (
                <p className="text-zinc-300 text-sm">
                  <strong>Email:</strong> {returnModal.borrower.email}
                </p>
              )}
            </div>

            <form onSubmit={handleReturnSubmit} className="space-y-4">
              {/* Return Items List */}
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <label className="block text-zinc-300 font-semibold">Items to Return</label>
                  {returnItems.length < returnModal.availableItems.length && (
                    <button
                      type="button"
                      onClick={handleAddReturnItem}
                      className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-white text-sm transition-colors"
                    >
                      + Add Another Item
                    </button>
                  )}
                </div>
                
                {returnItems.map((returnItem, index) => {
                  const item = returnItem.item;
                  const canRemove = returnItems.length > 1;
                  
                  return (
                    <div key={index} className="bg-zinc-900 p-4 rounded border border-zinc-700">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex-1">
                          <p className="text-white font-semibold mb-1">{item.component_name}</p>
                          <p className="text-zinc-400 text-sm">Remaining: {item.remaining_quantity}</p>
                        </div>
                        {canRemove && (
                          <button
                            type="button"
                            onClick={() => handleRemoveReturnItem(index)}
                            className="text-red-400 hover:text-red-300 text-lg font-bold"
                            title="Remove item"
                          >
                            ×
                          </button>
                        )}
                      </div>
                      
                      {/* Return All Option */}
                      <div className="flex items-center space-x-2 mb-3">
                        <input
                          type="checkbox"
                          id={`returnAll-${index}`}
                          checked={returnItem.returnAll}
                          onChange={(e) => handleReturnItemChange(index, 'returnAll', e.target.checked)}
                          className="w-4 h-4 text-green-600 bg-zinc-700 border-zinc-600 rounded focus:ring-green-500"
                        />
                        <label htmlFor={`returnAll-${index}`} className="text-white cursor-pointer text-sm">
                          Return all ({item.remaining_quantity})
                        </label>
                      </div>

                      {/* Quantity Input */}
                      {!returnItem.returnAll && (
                        <div className="mb-3">
                          <label className="block text-zinc-300 mb-1 text-sm">Quantity to Return</label>
                          <input
                            type="number"
                            min="1"
                            max={item.remaining_quantity}
                            value={returnItem.quantity}
                            onChange={(e) => handleReturnItemChange(index, 'quantity', e.target.value)}
                            className="w-full p-2 bg-zinc-700 border border-zinc-600 rounded text-white"
                            required={!returnItem.returnAll}
                            disabled={returnItem.returnAll}
                          />
                        </div>
                      )}

                      {/* Remarks for this item */}
                      <div>
                        <label className="block text-zinc-300 mb-1 text-sm">Remarks (Optional)</label>
                        <textarea
                          value={returnItem.remarks}
                          onChange={(e) => handleReturnItemChange(index, 'remarks', e.target.value)}
                          className="w-full p-2 bg-zinc-700 border border-zinc-600 rounded text-white text-sm"
                          rows="2"
                          placeholder="Enter remarks for this item..."
                        />
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* PIC Name (shared for all items) */}
              <div>
                <label className="block text-zinc-300 mb-1">PIC Name <span className="text-red-400">*</span></label>
                <input
                  type="text"
                  value={returnForm.pic_name}
                  onChange={(e) => handleReturnFormChange('pic_name', e.target.value)}
                  className="w-full p-2 bg-zinc-700 border border-zinc-600 rounded text-white"
                  required
                  placeholder="Enter PIC name (applies to all items)"
                />
                <p className="text-zinc-400 text-xs mt-1">This PIC will be used for all items in this return</p>
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
