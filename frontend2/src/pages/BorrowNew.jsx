import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { createBorrow } from '../api/borrow.api.js';
import { getAllComponents } from '../api/components.api.js';

// Searchable Component Dropdown
function SearchableComponentSelect({ components, value, onChange, required }) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
        setSearchTerm('');
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Filter components based on search term
  const filteredComponents = (components || []).filter(comp => 
    comp.name && comp.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Get selected component name
  const selectedComponent = value 
    ? components.find(c => c.id.toString() === value.toString())
    : null;
  const selectedName = selectedComponent ? selectedComponent.name : 'Select Component';

  // Calculate available quantity
  const getAvailableQuantity = (comp) => {
    return (comp.quantity || 0) - (comp.borrowed_quantity || 0);
  };

  const handleSelect = (componentId) => {
    onChange(componentId);
    setIsOpen(false);
    setSearchTerm('');
  };

  return (
    <div ref={dropdownRef} className="relative flex-1">
      {/* Dropdown Button/Input */}
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 bg-zinc-700 border border-zinc-600 rounded text-zinc-200 cursor-pointer flex justify-between items-center hover:border-zinc-500"
      >
        <span className={selectedComponent ? 'text-white' : 'text-zinc-400'}>
          {selectedName}
        </span>
        <span className="text-zinc-400">▼</span>
      </div>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-zinc-700 border border-zinc-600 rounded shadow-lg max-h-60 overflow-hidden">
          {/* Search Input */}
          <div className="p-2 border-b border-zinc-600">
            <input
              type="text"
              placeholder="Search components..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onClick={(e) => e.stopPropagation()}
              className="w-full p-2 bg-zinc-800 border border-zinc-600 rounded text-white placeholder-zinc-400 focus:outline-none focus:border-blue-500"
              autoFocus
            />
          </div>

          {/* Component List */}
          <div className="max-h-48 overflow-y-auto">
            {filteredComponents.length > 0 ? (
              filteredComponents.map((comp) => {
                const available = getAvailableQuantity(comp);
                return (
                  <div
                    key={comp.id}
                    onClick={() => handleSelect(comp.id)}
                    className={`p-3 cursor-pointer hover:bg-zinc-600 border-b border-zinc-600 ${
                      value && value.toString() === comp.id.toString() ? 'bg-zinc-600' : ''
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <span className="text-white font-medium">{comp.name}</span>
                      <span className="text-zinc-400 text-sm ml-2">
                        Available: {available}
                      </span>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="p-3 text-zinc-400 text-center">
                No components found
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default function BorrowNew() {
  const [formData, setFormData] = useState({
    borrower: { name: '', tp_id: '', phone: '', email: '' },
    items: [{ component_id: '', quantity: 1 }],
    reason: '',
    expected_return_date: new Date().toISOString().split('T')[0], // Today
    pic_name: ''
  });
  const [components, setComponents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState(''); // 'success' or 'error'
  const navigate = useNavigate();

  useEffect(() => {
    const fetchComponents = async () => {
      try {
        const data = await getAllComponents();
        setComponents(data);
      } catch (error) {
        console.error('Error fetching components:', error);
      }
    };
    fetchComponents();
  }, []);

  const handleBorrowerChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      borrower: { ...prev.borrower, [name]: value }
    }));
  };

  const handleItemChange = (index, field, value) => {
    const newItems = [...formData.items];
    newItems[index][field] = value;
    setFormData(prev => ({ ...prev, items: newItems }));
  };

  const addItem = () => {
    setFormData(prev => ({
      ...prev,
      items: [...prev.items, { component_id: '', quantity: 1 }]
    }));
  };

  const removeItem = (index) => {
    setFormData(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index)
    }));
  };

  const validateForm = () => {
    if (!formData.borrower.name || !formData.borrower.tp_id || !formData.borrower.phone || !formData.borrower.email) {
      setMessage('Borrower name, ID, phone, and email are mandatory.');
      return false;
    }
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.borrower.email)) {
      setMessage('Please enter a valid email address.');
      return false;
    }
    if (!formData.reason || !formData.pic_name) {
      setMessage('Reason and PIC name are mandatory.');
      return false;
    }
    for (const item of formData.items) {
      if (!item.component_id || item.quantity <= 0) {
        setMessage('Each item must have a component and positive quantity.');
        return false;
      }
      const comp = components.find(c => c.id == item.component_id);
      if (comp) {
        const available = (comp.available_quantity || 0);
        if (item.quantity > available) {
          setMessage(`Quantity for ${comp.name} exceeds available. Available: ${available}, Requested: ${item.quantity}`);
          return false;
        }
      }
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    setLoading(true);
    try {
      const dataToSend = {
        ...formData,
        items: formData.items.map(item => ({
          component_id: parseInt(item.component_id),
          quantity: parseInt(item.quantity)
        }))
      };
      await createBorrow(dataToSend);
      setMessage('Borrow created successfully!');
      setMessageType('success');
      // Reset form
      setFormData({
        borrower: { name: '', tp_id: '', phone: '', email: '' },
        items: [{ component_id: '', quantity: 1 }],
        reason: '',
        expected_return_date: new Date().toISOString().split('T')[0],
        pic_name: ''
      });
      // Redirect to active borrows after a short delay
      setTimeout(() => navigate('/borrow/active'), 2000);
    } catch (error) {
      setMessage('Error creating borrow: ' + error.message);
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-zinc-900 text-zinc-200 min-h-screen">
      <h1 className="text-2xl font-bold mb-4">New Borrow</h1>
      <form onSubmit={handleSubmit} className="space-y-4 bg-zinc-800 p-6 rounded-lg border border-zinc-700">
        <div>
          <h2 className="text-lg font-semibold mb-2">Borrower</h2>
          <input
            type="text"
            name="name"
            placeholder="Name"
            value={formData.borrower.name}
            onChange={handleBorrowerChange}
            className="w-full p-2 bg-zinc-700 border border-zinc-600 rounded text-zinc-200 placeholder-zinc-400"
            required
          />
          <input
            type="text"
            name="tp_id"
            placeholder="TP ID"
            value={formData.borrower.tp_id}
            onChange={handleBorrowerChange}
            className="w-full p-2 bg-zinc-700 border border-zinc-600 rounded mt-2 text-zinc-200 placeholder-zinc-400"
            required
          />
          <input
            type="tel"
            name="phone"
            placeholder="Phone"
            value={formData.borrower.phone}
            onChange={handleBorrowerChange}
            className="w-full p-2 bg-zinc-700 border border-zinc-600 rounded mt-2 text-zinc-200 placeholder-zinc-400"
            required
          />
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.borrower.email}
            onChange={handleBorrowerChange}
            className="w-full p-2 bg-zinc-700 border border-zinc-600 rounded mt-2 text-zinc-200 placeholder-zinc-400"
            required
          />
        </div>
        <div>
          <h2 className="text-lg font-semibold mb-2">Items</h2>
          {formData.items.map((item, index) => (
            <div key={index} className="flex space-x-2 mb-2">
              <SearchableComponentSelect
                components={components}
                value={item.component_id}
                onChange={(componentId) => handleItemChange(index, 'component_id', componentId)}
                required
              />
              <input
                type="number"
                min="1"
                value={item.quantity}
                onChange={(e) => handleItemChange(index, 'quantity', parseInt(e.target.value) || 1)}
                className="w-20 p-2 bg-zinc-700 border border-zinc-600 rounded text-zinc-200"
                required
              />
              <button type="button" onClick={() => removeItem(index)} className="px-2 py-1 bg-red-600 hover:bg-red-700 rounded text-white">Remove</button>
            </div>
          ))}
          <button type="button" onClick={addItem} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white">Add Item</button>
        </div>
        <div>
          <label className="block mb-1">Reason</label>
          <textarea
            value={formData.reason}
            onChange={(e) => setFormData(prev => ({ ...prev, reason: e.target.value }))}
            className="w-full p-2 bg-zinc-700 border border-zinc-600 rounded text-zinc-200 placeholder-zinc-400"
            required
          />
        </div>
        <div>
          <label className="block mb-1">Expected Return Date</label>
          <input
            type="date"
            value={formData.expected_return_date}
            onChange={(e) => setFormData(prev => ({ ...prev, expected_return_date: e.target.value }))}
            className="w-full p-2 bg-zinc-700 border border-zinc-600 rounded text-zinc-200"
            required
          />
        </div>
        <div>
          <label className="block mb-1">PIC Name</label>
          <input
            type="text"
            value={formData.pic_name}
            onChange={(e) => setFormData(prev => ({ ...prev, pic_name: e.target.value }))}
            className="w-full p-2 bg-zinc-700 border border-zinc-600 rounded text-zinc-200 placeholder-zinc-400"
            required
          />
        </div>
        <button type="submit" disabled={loading} className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-white">
          {loading ? 'Submitting...' : 'Submit Borrow'}
        </button>
      </form>
      {message && (
        <p className={`mt-4 text-xl font-bold p-4 rounded ${messageType === 'success' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'}`}>
          {message}
        </p>
      )}
    </div>
  );
}