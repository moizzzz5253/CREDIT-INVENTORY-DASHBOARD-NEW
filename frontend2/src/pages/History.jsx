import React, { useState, useEffect } from 'react';
import { getReturnHistory, getDeletedComponentsHistory } from '../api/history.api.js';
import { getCategories } from '../api/components.api.js';

export default function History() {
  const [activeTab, setActiveTab] = useState('returned'); // 'returned' or 'deleted'
  const [history, setHistory] = useState([]);
  const [filteredHistory, setFilteredHistory] = useState([]);
  const [deletedComponents, setDeletedComponents] = useState([]);
  const [filteredDeletedComponents, setFilteredDeletedComponents] = useState([]);
  const [categories, setCategories] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [dateFilter, setDateFilter] = useState('all'); // 'all', '1month', '6months', '1year'
  const [expandedCards, setExpandedCards] = useState(new Set());
  const [loading, setLoading] = useState(false);

  // Fetch history data
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        if (activeTab === 'returned') {
          const [historyData, categoriesData] = await Promise.all([
            getReturnHistory(),
            getCategories()
          ]);
          setHistory(historyData);
          setCategories(categoriesData);
        } else if (activeTab === 'deleted') {
          const [deletedData, categoriesData] = await Promise.all([
            getDeletedComponentsHistory(),
            getCategories()
          ]);
          setDeletedComponents(deletedData);
          setCategories(categoriesData);
        }
      } catch (error) {
        console.error('Error fetching history:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [activeTab]);

  // Filter returned history based on search, category, and date
  useEffect(() => {
    if (activeTab !== 'returned') return;

    let filtered = [...history];

    // Search filter (only search by component name, borrower name, and returned_by PIC)
    if (searchTerm.trim()) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(item =>
        item.component_name.toLowerCase().includes(searchLower) ||
        item.borrower_name.toLowerCase().includes(searchLower) ||
        (item.returned_by && item.returned_by.toLowerCase().includes(searchLower))
      );
    }

    // Category filter
    if (selectedCategory) {
      filtered = filtered.filter(item => item.component_category === selectedCategory);
    }

    // Date filter
    if (dateFilter !== 'all') {
      const now = new Date();
      let cutoffDate = new Date();

      switch (dateFilter) {
        case '1month':
          cutoffDate.setMonth(now.getMonth() - 1);
          break;
        case '6months':
          cutoffDate.setMonth(now.getMonth() - 6);
          break;
        case '1year':
          cutoffDate.setFullYear(now.getFullYear() - 1);
          break;
        default:
          break;
      }

      filtered = filtered.filter(item => {
        if (!item.returned_at) return false;
        const returnedDate = new Date(item.returned_at);
        return returnedDate >= cutoffDate;
      });
    }

    setFilteredHistory(filtered);
  }, [history, searchTerm, selectedCategory, dateFilter, activeTab]);

  // Filter deleted components based on search, category, and date
  useEffect(() => {
    if (activeTab !== 'deleted') return;

    let filtered = [...deletedComponents];

    // Search filter (search by component name)
    if (searchTerm.trim()) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(item =>
        item.component_name.toLowerCase().includes(searchLower)
      );
    }

    // Category filter
    if (selectedCategory) {
      filtered = filtered.filter(item => item.category === selectedCategory);
    }

    // Date filter (based on deleted_at)
    if (dateFilter !== 'all') {
      const now = new Date();
      let cutoffDate = new Date();

      switch (dateFilter) {
        case '1month':
          cutoffDate.setMonth(now.getMonth() - 1);
          break;
        case '6months':
          cutoffDate.setMonth(now.getMonth() - 6);
          break;
        case '1year':
          cutoffDate.setFullYear(now.getFullYear() - 1);
          break;
        default:
          break;
      }

      filtered = filtered.filter(item => {
        if (!item.deleted_at) return false;
        const deletedDate = new Date(item.deleted_at);
        return deletedDate >= cutoffDate;
      });
    }

    setFilteredDeletedComponents(filtered);
  }, [deletedComponents, searchTerm, selectedCategory, dateFilter, activeTab]);

  // Toggle card expansion
  const toggleCard = (uniqueKey) => {
    setExpandedCards(prev => {
      const next = new Set(prev);
      if (next.has(uniqueKey)) {
        next.delete(uniqueKey);
      } else {
        next.add(uniqueKey);
      }
      return next;
    });
  };

  // Format date with time (displays in local timezone)
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      // Ensure UTC timezone indicator if not present (naive datetime strings from backend)
      let dateStr = dateString;
      if (!dateStr.endsWith('Z') && !dateStr.includes('+') && !dateStr.includes('-', 10)) {
        dateStr = dateStr + 'Z';
      }
      // Parse ISO string - JavaScript Date automatically converts UTC to local timezone
      const date = new Date(dateStr);
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      });
    } catch (e) {
      return 'Invalid Date';
    }
  };

  // Format date only (without time)
  const formatDateOnly = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch (e) {
      return 'Invalid Date';
    }
  };

  return (
    <div className="p-6 bg-zinc-900 text-zinc-200 min-h-screen">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">History</h1>
      </div>

      {/* Tabs */}
      <div className="flex space-x-4 mb-6 border-b border-zinc-700">
        <button
          onClick={() => {
            setActiveTab('returned');
            setSearchTerm('');
            setSelectedCategory('');
            setDateFilter('all');
          }}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'returned'
              ? 'text-white border-b-2 border-blue-500'
              : 'text-zinc-400 hover:text-white'
          }`}
        >
          Returned Components
        </button>
        <button
          onClick={() => {
            setActiveTab('deleted');
            setSearchTerm('');
            setSelectedCategory('');
            setDateFilter('all');
          }}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'deleted'
              ? 'text-white border-b-2 border-blue-500'
              : 'text-zinc-400 hover:text-white'
          }`}
        >
          Deleted Items
        </button>
      </div>

      {activeTab === 'returned' && (
        <>
          {/* Filters */}
          <div className="bg-zinc-800 p-4 rounded-lg border border-zinc-700 mb-6 space-y-4">
            {/* Search Bar */}
            <div>
              <input
                type="text"
                placeholder="Search by component name, borrower name, or PIC (returned)..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full p-2 bg-zinc-700 border border-zinc-600 rounded text-white placeholder-zinc-400 focus:outline-none focus:border-blue-500"
              />
            </div>

            {/* Category and Date Filters */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Category Filter */}
              <div>
                <label className="block text-zinc-300 mb-1">Category</label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full p-2 bg-zinc-700 border border-zinc-600 rounded text-white"
                >
                  <option value="">All Categories</option>
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>

              {/* Date Filter */}
              <div>
                <label className="block text-zinc-300 mb-1">Date Range</label>
                <select
                  value={dateFilter}
                  onChange={(e) => setDateFilter(e.target.value)}
                  className="w-full p-2 bg-zinc-700 border border-zinc-600 rounded text-white"
                >
                  <option value="all">All Time</option>
                  <option value="1month">Last 1 Month</option>
                  <option value="6months">Last 6 Months</option>
                  <option value="1year">Last 1 Year</option>
                </select>
              </div>
            </div>
          </div>

          {/* History List */}
          {loading ? (
            <div className="text-center text-zinc-400 py-8">Loading...</div>
          ) : filteredHistory.length === 0 ? (
            <div className="text-center text-zinc-400 py-8">
              {history.length === 0 ? 'No return history found' : 'No results match your filters'}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredHistory.map((item, index) => {
                // Create a unique key based on item data
                const uniqueKey = `${item.returned_at || 'unknown'}-${item.component_name}-${item.borrower_name}-${item.returned_qty}-${index}`;
                const isExpanded = expandedCards.has(uniqueKey);

                return (
                  <div
                    key={uniqueKey}
                    className="bg-zinc-800 rounded-xl p-4 border border-zinc-700 transition-all duration-200 hover:shadow-lg"
                  >
                    {/* Card Header - Clickable */}
                    <div
                      className="cursor-pointer"
                      onClick={() => toggleCard(uniqueKey)}
                    >
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex-1">
                          <h3 className="font-semibold text-white text-lg mb-1">
                            {item.component_name}
                          </h3>
                          <p className="text-zinc-300 text-sm">
                            <strong>Qty Returned:</strong> {item.returned_qty}
                          </p>
                          <p className="text-zinc-300 text-sm">
                            <strong>Borrower:</strong> {item.borrower_name}
                          </p>
                          <p className="text-zinc-300 text-sm">
                            <strong>PIC (Returned):</strong> {item.returned_by || 'N/A'}
                          </p>
                          <p className="text-zinc-400 text-sm mt-2">
                            Returned: {formatDate(item.returned_at)}
                          </p>
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
                    </div>

                    {/* Expanded Content */}
                    {isExpanded && (
                      <div className="mt-4 pt-4 border-t border-zinc-600 space-y-2">
                        <div className="bg-zinc-900 p-3 rounded border border-zinc-700">
                          <p className="text-zinc-300 text-sm mb-1">
                            <strong>Borrowed At:</strong> <span className="text-base">{formatDate(item.borrowed_at)}</span>
                          </p>
                          <p className="text-zinc-300 text-sm mb-1">
                            <strong>TP ID:</strong> {item.tp_id}
                          </p>
                          <p className="text-zinc-300 text-sm mb-1">
                            <strong>Phone:</strong> {item.phone}
                          </p>
                          <p className="text-zinc-300 text-sm mb-1">
                            <strong>PIC (Borrowed):</strong> {item.borrowed_by_pic || 'N/A'}
                          </p>
                          <p className="text-zinc-300 text-sm mb-1">
                            <strong>Quantity Borrowed:</strong> {item.borrowed_qty}
                          </p>
                          <p className="text-zinc-300 text-sm mb-1">
                            <strong>Expected Return:</strong> <span className="text-base">{formatDateOnly(item.expected_return_date)}</span>
                          </p>
                          {item.remarks && (
                            <p className="text-zinc-300 text-sm">
                              <strong>Remarks:</strong> {item.remarks}
                            </p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}

      {activeTab === 'deleted' && (
        <>
          {/* Filters */}
          <div className="bg-zinc-800 p-4 rounded-lg border border-zinc-700 mb-6 space-y-4">
            {/* Search Bar */}
            <div>
              <input
                type="text"
                placeholder="Search by component name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full p-2 bg-zinc-700 border border-zinc-600 rounded text-white placeholder-zinc-400 focus:outline-none focus:border-blue-500"
              />
            </div>

            {/* Category and Date Filters */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Category Filter */}
              <div>
                <label className="block text-zinc-300 mb-1">Category</label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full p-2 bg-zinc-700 border border-zinc-600 rounded text-white"
                >
                  <option value="">All Categories</option>
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>

              {/* Date Filter */}
              <div>
                <label className="block text-zinc-300 mb-1">Date Range</label>
                <select
                  value={dateFilter}
                  onChange={(e) => setDateFilter(e.target.value)}
                  className="w-full p-2 bg-zinc-700 border border-zinc-600 rounded text-white"
                >
                  <option value="all">All Time</option>
                  <option value="1month">Last 1 Month</option>
                  <option value="6months">Last 6 Months</option>
                  <option value="1year">Last 1 Year</option>
                </select>
              </div>
            </div>
          </div>

          {/* Deleted Components List */}
          {loading ? (
            <div className="text-center text-zinc-400 py-8">Loading...</div>
          ) : filteredDeletedComponents.length === 0 ? (
            <div className="text-center text-zinc-400 py-8">
              {deletedComponents.length === 0 ? 'No deleted components found' : 'No results match your filters'}
            </div>
          ) : (
            <div className="bg-zinc-800 rounded-lg border border-zinc-700 overflow-hidden">
              {/* Table Header */}
              <div className="grid grid-cols-12 gap-4 p-4 bg-zinc-900 border-b border-zinc-700 font-semibold text-white text-sm">
                <div className="col-span-2">Component Name</div>
                <div className="col-span-1 text-center">Qty</div>
                <div className="col-span-2">Category</div>
                <div className="col-span-2">Container</div>
                <div className="col-span-1">Date Added</div>
                <div className="col-span-1">Date Deleted</div>
                <div className="col-span-3">Reason for remove/delete</div>
              </div>

              {/* Table Rows */}
              <div className="divide-y divide-zinc-700">
                {filteredDeletedComponents.map((item, index) => (
                  <div
                    key={item.component_id || index}
                    className="grid grid-cols-12 gap-4 p-4 hover:bg-zinc-900 transition-colors text-sm"
                  >
                    <div className="col-span-2 text-white font-medium">
                      {item.component_name}
                    </div>
                    <div className="col-span-1 text-center text-zinc-300">
                      {item.quantity}
                    </div>
                    <div className="col-span-2 text-zinc-300">
                      {item.category}
                    </div>
                    <div className="col-span-2 text-zinc-300">
                      {item.container}
                    </div>
                    <div className="col-span-1 text-zinc-400 text-sm">
                      {formatDateOnly(item.added_at)}
                    </div>
                    <div className="col-span-1 text-zinc-400 text-sm">
                      {formatDate(item.deleted_at)}
                    </div>
                    <div className="col-span-3 text-zinc-300">
                      {item.reason || 'N/A'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

