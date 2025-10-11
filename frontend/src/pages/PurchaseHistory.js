import React, { useState, useEffect } from 'react';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Download,
  Filter,
  Search,
  Calendar
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

export const PurchaseHistory = () => {
  const { user } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const itemsPerPage = 10;

  useEffect(() => {
    fetchTransactions();
  }, [filter, currentPage]);

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const params = {
        limit: itemsPerPage,
        skip: (currentPage - 1) * itemsPerPage
      };

      if (filter !== 'all') {
        params.status = filter;
      }

      const response = await axios.get(
        `${BACKEND_URL}/api/payments/history/list`,
        {
          headers: { Authorization: `Bearer ${token}` },
          params
        }
      );

      setTransactions(response.data.transactions || []);
      setTotalCount(response.data.total || 0);
    } catch (error) {
      console.error('Failed to fetch transactions:', error);
      toast.error('Failed to load purchase history');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      paid: {
        icon: CheckCircle,
        color: 'green',
        bg: 'bg-green-100',
        text: 'text-green-800',
        label: 'Paid'
      },
      pending: {
        icon: Clock,
        color: 'yellow',
        bg: 'bg-yellow-100',
        text: 'text-yellow-800',
        label: 'Pending'
      },
      failed: {
        icon: XCircle,
        color: 'red',
        bg: 'bg-red-100',
        text: 'text-red-800',
        label: 'Failed'
      },
      expired: {
        icon: AlertCircle,
        color: 'gray',
        bg: 'bg-gray-100',
        text: 'text-gray-800',
        label: 'Expired'
      },
      cancelled: {
        icon: XCircle,
        color: 'gray',
        bg: 'bg-gray-100',
        text: 'text-gray-800',
        label: 'Cancelled'
      }
    };

    const config = statusConfig[status] || statusConfig.pending;
    const Icon = config.icon;

    return (
      <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium ${config.bg} ${config.text}`}>
        <Icon size={16} />
        {config.label}
      </span>
    );
  };

  const getPaymentMethodLabel = (method) => {
    const methods = {
      midtrans: 'Midtrans',
      xendit_va: 'Virtual Account',
      xendit_qris: 'QRIS',
      xendit_ewallet: 'E-wallet'
    };
    return methods[method] || method;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('id-ID', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const filteredTransactions = transactions.filter(tx =>
    tx.reference_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    tx.customer_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalPages = Math.ceil(totalCount / itemsPerPage);

  return (
    <Layout>
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Purchase History
          </h1>
          <p className="text-gray-600">
            View all your water balance top-up transactions
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search by reference ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Status Filter */}
            <div className="flex items-center gap-2">
              <Filter size={20} className="text-gray-400" />
              <select
                value={filter}
                onChange={(e) => {
                  setFilter(e.target.value);
                  setCurrentPage(1);
                }}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Status</option>
                <option value="paid">Paid</option>
                <option value="pending">Pending</option>
                <option value="failed">Failed</option>
                <option value="expired">Expired</option>
              </select>
            </div>
          </div>
        </div>

        {/* Transactions List */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="p-12 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-gray-600 mt-4">Loading transactions...</p>
            </div>
          ) : filteredTransactions.length === 0 ? (
            <div className="p-12 text-center">
              <Calendar className="mx-auto text-gray-400 mb-4" size={48} />
              <p className="text-gray-600 text-lg mb-2">No transactions found</p>
              <p className="text-gray-500">Your purchase history will appear here</p>
            </div>
          ) : (
            <>
              {/* Desktop Table */}
              <div className="hidden md:block overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Reference ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Payment Method
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Amount
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Water Volume
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredTransactions.map((tx) => (
                      <tr key={tx.reference_id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatDate(tx.created_at)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm font-mono text-gray-600">
                            {tx.reference_id}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {getPaymentMethodLabel(tx.payment_method)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                          Rp {tx.amount.toLocaleString('id-ID')}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {(tx.amount / 10000).toFixed(1)} m³
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {getStatusBadge(tx.status)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <button
                            onClick={() => window.location.href = `/purchase-receipt/${tx.reference_id}`}
                            className="text-blue-600 hover:text-blue-800 font-medium"
                          >
                            View Details
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Mobile Cards */}
              <div className="md:hidden divide-y divide-gray-200">
                {filteredTransactions.map((tx) => (
                  <div key={tx.reference_id} className="p-4">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <p className="font-semibold text-gray-900 mb-1">
                          Rp {tx.amount.toLocaleString('id-ID')}
                        </p>
                        <p className="text-sm text-gray-600">
                          {(tx.amount / 10000).toFixed(1)} m³
                        </p>
                      </div>
                      {getStatusBadge(tx.status)}
                    </div>
                    <div className="space-y-1 text-sm">
                      <p className="text-gray-600">
                        {getPaymentMethodLabel(tx.payment_method)}
                      </p>
                      <p className="text-gray-500 text-xs">
                        {formatDate(tx.created_at)}
                      </p>
                      <p className="text-gray-500 font-mono text-xs">
                        {tx.reference_id}
                      </p>
                    </div>
                    <button
                      onClick={() => window.location.href = `/purchase-receipt/${tx.reference_id}`}
                      className="mt-3 text-blue-600 hover:text-blue-800 font-medium text-sm"
                    >
                      View Details →
                    </button>
                  </div>
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
                  <div className="text-sm text-gray-700">
                    Showing {((currentPage - 1) * itemsPerPage) + 1} to {Math.min(currentPage * itemsPerPage, totalCount)} of {totalCount} transactions
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                      className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Previous
                    </button>
                    <button
                      onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                      className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Next
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </Layout>
  );
};
