import React, { useState, useEffect } from 'react';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';
import toast from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Plus, 
  Ticket, 
  Calendar,
  Users,
  TrendingUp,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  Clock,
  Eye,
  AlertCircle,
  Tag,
  Percent,
  DollarSign
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || window.location.origin;
const API = `${BACKEND_URL}/api`;

const VoucherManagement = () => {
  const { user } = useAuth();
  const [vouchers, setVouchers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filter, setFilter] = useState('all'); // all, active, expired, depleted
  const [formData, setFormData] = useState({
    code: '',
    description: '',
    discount_type: 'percentage',
    discount_value: '',
    min_purchase_amount: '',
    max_discount_amount: '',
    usage_limit: '',
    per_customer_limit: '1',
    valid_from: '',
    valid_until: ''
  });

  useEffect(() => {
    fetchVouchers();
  }, [filter]);

  const fetchVouchers = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const url = filter === 'all' 
        ? `${API}/vouchers` 
        : `${API}/vouchers?status=${filter}`;
      
      const response = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setVouchers(response.data || []);
    } catch (error) {
      console.error('Failed to fetch vouchers:', error);
      toast.error('Failed to load vouchers', { id: 'voucher-load-error' });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateVoucher = async (e) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('token');
      const payload = {
        ...formData,
        discount_value: parseFloat(formData.discount_value),
        min_purchase_amount: parseFloat(formData.min_purchase_amount) || 0,
        max_discount_amount: formData.max_discount_amount ? parseFloat(formData.max_discount_amount) : null,
        usage_limit: formData.usage_limit ? parseInt(formData.usage_limit) : null,
        per_customer_limit: parseInt(formData.per_customer_limit),
        valid_from: new Date(formData.valid_from).toISOString(),
        valid_until: new Date(formData.valid_until).toISOString()
      };

      await axios.post(`${API}/vouchers`, payload, {
        headers: { Authorization: `Bearer ${token}` }
      });

      toast.success('Voucher created successfully!');
      setShowCreateModal(false);
      resetForm();
      fetchVouchers();
    } catch (error) {
      console.error('Failed to create voucher:', error);
      toast.error(error.response?.data?.detail || 'Failed to create voucher');
    }
  };

  const handleUpdateStatus = async (voucherId, newStatus) => {
    try {
      const token = localStorage.getItem('token');
      await axios.patch(
        `${API}/vouchers/${voucherId}/status?new_status=${newStatus}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Voucher status updated');
      fetchVouchers();
    } catch (error) {
      console.error('Failed to update status:', error);
      toast.error('Failed to update voucher status');
    }
  };

  const resetForm = () => {
    setFormData({
      code: '',
      description: '',
      discount_type: 'percentage',
      discount_value: '',
      min_purchase_amount: '',
      max_discount_amount: '',
      usage_limit: '',
      per_customer_limit: '1',
      valid_from: '',
      valid_until: ''
    });
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0
    }).format(value || 0);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('id-ID', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStatusBadge = (voucher) => {
    const now = new Date();
    const validUntil = new Date(voucher.valid_until);
    
    if (voucher.status === 'depleted') {
      return <span className="px-3 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-700">Depleted</span>;
    }
    if (voucher.status === 'inactive') {
      return <span className="px-3 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-700">Inactive</span>;
    }
    if (now > validUntil) {
      return <span className="px-3 py-1 rounded-full text-xs font-semibold bg-orange-100 text-orange-700">Expired</span>;
    }
    return <span className="px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-700">Active</span>;
  };

  const getDiscountDisplay = (voucher) => {
    if (voucher.discount_type === 'percentage') {
      return `${voucher.discount_value}% OFF`;
    }
    return `${formatCurrency(voucher.discount_value)} OFF`;
  };

  const getUsagePercentage = (voucher) => {
    if (!voucher.usage_limit) return 0;
    return (voucher.usage_count / voucher.usage_limit) * 100;
  };

  if (user?.role !== 'admin') {
    return (
      <Layout>
        <div className="text-center py-12">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900">Access Denied</h2>
          <p className="text-gray-600 mt-2">Only admins can manage vouchers</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Voucher Management</h1>
            <p className="text-gray-600 mt-1">Create and manage promotional discount vouchers</p>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowCreateModal(true)}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg shadow-lg transition"
          >
            <Plus className="w-5 h-5" />
            <span>Create Voucher</span>
          </motion.button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm">Total Vouchers</p>
                <p className="text-3xl font-bold mt-2">{vouchers.length}</p>
              </div>
              <Ticket className="w-12 h-12 text-blue-200" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100 text-sm">Active</p>
                <p className="text-3xl font-bold mt-2">
                  {vouchers.filter(v => v.status === 'active').length}
                </p>
              </div>
              <CheckCircle className="w-12 h-12 text-green-200" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl shadow-lg p-6 text-white"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-100 text-sm">Expired</p>
                <p className="text-3xl font-bold mt-2">
                  {vouchers.filter(v => v.status === 'expired').length}
                </p>
              </div>
              <Clock className="w-12 h-12 text-orange-200" />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg p-6 text-white"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm">Total Usage</p>
                <p className="text-3xl font-bold mt-2">
                  {vouchers.reduce((sum, v) => sum + v.usage_count, 0)}
                </p>
              </div>
              <Users className="w-12 h-12 text-purple-200" />
            </div>
          </motion.div>
        </div>

        {/* Filters */}
        <div className="flex space-x-2">
          {['all', 'active', 'expired', 'depleted', 'inactive'].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                filter === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>

        {/* Vouchers List */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <motion.div 
              className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full"
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            />
          </div>
        ) : vouchers.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <Ticket className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No vouchers found</h3>
            <p className="text-gray-600">Create your first promotional voucher to get started</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6">
            <AnimatePresence>
              {vouchers.map((voucher, index) => (
                <motion.div
                  key={voucher.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ delay: index * 0.05 }}
                  className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition"
                >
                  <div className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-3">
                          <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
                            <Tag className="w-6 h-6 text-white" />
                          </div>
                          <div>
                            <div className="flex items-center space-x-3">
                              <h3 className="text-xl font-bold text-gray-900">{voucher.code}</h3>
                              {getStatusBadge(voucher)}
                            </div>
                            <p className="text-gray-600 text-sm mt-1">{voucher.description}</p>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
                          <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                            <div className="flex items-center space-x-2 text-green-700 mb-1">
                              {voucher.discount_type === 'percentage' ? (
                                <Percent className="w-4 h-4" />
                              ) : (
                                <DollarSign className="w-4 h-4" />
                              )}
                              <span className="text-xs font-medium">Discount</span>
                            </div>
                            <p className="text-2xl font-bold text-green-900">{getDiscountDisplay(voucher)}</p>
                          </div>

                          <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                            <div className="flex items-center space-x-2 text-blue-700 mb-1">
                              <Users className="w-4 h-4" />
                              <span className="text-xs font-medium">Usage</span>
                            </div>
                            <p className="text-2xl font-bold text-blue-900">
                              {voucher.usage_count} / {voucher.usage_limit || '∞'}
                            </p>
                            {voucher.usage_limit && (
                              <div className="w-full bg-blue-200 rounded-full h-2 mt-2">
                                <div 
                                  className="bg-blue-600 h-2 rounded-full transition-all"
                                  style={{ width: `${Math.min(getUsagePercentage(voucher), 100)}%` }}
                                />
                              </div>
                            )}
                          </div>

                          <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                            <div className="flex items-center space-x-2 text-purple-700 mb-1">
                              <DollarSign className="w-4 h-4" />
                              <span className="text-xs font-medium">Min Purchase</span>
                            </div>
                            <p className="text-lg font-bold text-purple-900">
                              {formatCurrency(voucher.min_purchase_amount)}
                            </p>
                          </div>

                          <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
                            <div className="flex items-center space-x-2 text-orange-700 mb-1">
                              <Calendar className="w-4 h-4" />
                              <span className="text-xs font-medium">Valid Until</span>
                            </div>
                            <p className="text-sm font-bold text-orange-900">
                              {formatDate(voucher.valid_until)}
                            </p>
                          </div>
                        </div>

                        {voucher.max_discount_amount && (
                          <div className="mt-3 text-sm text-gray-600">
                            <span className="font-medium">Max Discount:</span> {formatCurrency(voucher.max_discount_amount)}
                          </div>
                        )}
                      </div>

                      <div className="flex flex-col space-y-2 ml-4">
                        {voucher.status === 'active' && (
                          <button
                            onClick={() => handleUpdateStatus(voucher.id, 'inactive')}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                            title="Deactivate"
                          >
                            <XCircle className="w-5 h-5" />
                          </button>
                        )}
                        {voucher.status === 'inactive' && (
                          <button
                            onClick={() => handleUpdateStatus(voucher.id, 'active')}
                            className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition"
                            title="Activate"
                          >
                            <CheckCircle className="w-5 h-5" />
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* Create Voucher Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-2xl font-bold text-gray-900">Create New Voucher</h2>
                <p className="text-gray-600 mt-1">Fill in the details to create a promotional voucher</p>
              </div>

              <form onSubmit={handleCreateVoucher} className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Voucher Code *
                    </label>
                    <input
                      type="text"
                      value={formData.code}
                      onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase() })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="e.g., WELCOME50"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Discount Type *
                    </label>
                    <select
                      value={formData.discount_type}
                      onChange={(e) => setFormData({ ...formData, discount_type: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="percentage">Percentage</option>
                      <option value="fixed_amount">Fixed Amount</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description *
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    rows="2"
                    placeholder="e.g., Welcome bonus for new customers"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Discount Value * {formData.discount_type === 'percentage' ? '(%)' : '(IDR)'}
                    </label>
                    <input
                      type="number"
                      value={formData.discount_value}
                      onChange={(e) => setFormData({ ...formData, discount_value: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder={formData.discount_type === 'percentage' ? '50' : '100000'}
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Min Purchase Amount (IDR)
                    </label>
                    <input
                      type="number"
                      value={formData.min_purchase_amount}
                      onChange={(e) => setFormData({ ...formData, min_purchase_amount: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="50000"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Max Discount Amount (IDR)
                    </label>
                    <input
                      type="number"
                      value={formData.max_discount_amount}
                      onChange={(e) => setFormData({ ...formData, max_discount_amount: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="100000 (optional)"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Total Usage Limit
                    </label>
                    <input
                      type="number"
                      value={formData.usage_limit}
                      onChange={(e) => setFormData({ ...formData, usage_limit: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="100 (blank for unlimited)"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Per Customer Limit *
                  </label>
                  <input
                    type="number"
                    value={formData.per_customer_limit}
                    onChange={(e) => setFormData({ ...formData, per_customer_limit: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="1"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Valid From *
                    </label>
                    <input
                      type="datetime-local"
                      value={formData.valid_from}
                      onChange={(e) => setFormData({ ...formData, valid_from: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Valid Until *
                    </label>
                    <input
                      type="datetime-local"
                      value={formData.valid_until}
                      onChange={(e) => setFormData({ ...formData, valid_until: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      required
                    />
                  </div>
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreateModal(false);
                      resetForm();
                    }}
                    className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
                  >
                    Create Voucher
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </Layout>
  );
};

export default VoucherManagement;
