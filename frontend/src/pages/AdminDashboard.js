import React, { useState, useEffect } from 'react';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  Users,
  Droplet,
  DollarSign,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  XCircle,
  Activity,
  CreditCard,
  UserCheck,
  Building2
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

export const AdminDashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [recentTransactions, setRecentTransactions] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      // Fetch payment statistics
      const statsResponse = await axios.get(
        `${BACKEND_URL}/api/admin/payment-settings/statistics`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setStats(statsResponse.data);

      // Fetch recent transactions
      const transactionsResponse = await axios.get(
        `${BACKEND_URL}/api/payments/history/list?limit=5`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setRecentTransactions(transactionsResponse.data.transactions || []);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      toast.error('Failed to load dashboard data', { id: 'dashboard-load-error' });
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return `Rp ${amount.toLocaleString('id-ID')}`;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('id-ID', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStatusBadge = (status) => {
    const configs = {
      paid: { bg: 'bg-green-100', text: 'text-green-800', label: 'Paid' },
      pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Pending' },
      failed: { bg: 'bg-red-100', text: 'text-red-800', label: 'Failed' },
      expired: { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Expired' }
    };
    const config = configs[status] || configs.pending;
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
        {config.label}
      </span>
    );
  };

  if (loading) {
    return (
      <Layout>
        <div className="p-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 mt-4 text-center">Loading dashboard...</p>
          </div>
        </div>
      </Layout>
    );
  }

  const statCards = [
    {
      title: 'Total Revenue',
      value: stats?.total_revenue ? formatCurrency(stats.total_revenue) : 'Rp 0',
      icon: DollarSign,
      color: 'blue',
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-600',
      description: 'From successful payments'
    },
    {
      title: 'Total Transactions',
      value: stats?.total_transactions || 0,
      icon: CreditCard,
      color: 'purple',
      bgColor: 'bg-purple-50',
      iconColor: 'text-purple-600',
      description: 'All payment transactions'
    },
    {
      title: 'Successful Payments',
      value: stats?.successful_payments || 0,
      icon: CheckCircle,
      color: 'green',
      bgColor: 'bg-green-50',
      iconColor: 'text-green-600',
      description: 'Completed transactions'
    },
    {
      title: 'Pending Payments',
      value: stats?.pending_payments || 0,
      icon: Clock,
      color: 'yellow',
      bgColor: 'bg-yellow-50',
      iconColor: 'text-yellow-600',
      description: 'Awaiting payment'
    },
    {
      title: 'Total Customers',
      value: stats?.total_customers || 0,
      icon: Users,
      color: 'indigo',
      bgColor: 'bg-indigo-50',
      iconColor: 'text-indigo-600',
      description: 'Registered customers'
    },
    {
      title: 'Active Technicians',
      value: stats?.total_technicians || 0,
      icon: UserCheck,
      color: 'teal',
      bgColor: 'bg-teal-50',
      iconColor: 'text-teal-600',
      description: 'Field technicians'
    }
  ];

  return (
    <Layout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Admin Dashboard
          </h1>
          <p className="text-gray-600">
            Overview of IndoWater system statistics and recent activities
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {statCards.map((stat, index) => (
            <div
              key={index}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <stat.icon className={stat.iconColor} size={24} />
                </div>
              </div>
              <h3 className="text-sm font-medium text-gray-600 mb-1">{stat.title}</h3>
              <p className="text-3xl font-bold text-gray-900 mb-1">{stat.value}</p>
              <p className="text-xs text-gray-500">{stat.description}</p>
            </div>
          ))}
        </div>

        {/* Payment Method Breakdown */}
        {stats?.payment_method_stats && stats.payment_method_stats.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
              <Activity size={20} className="text-blue-600" />
              Payment Methods Distribution
            </h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              {stats.payment_method_stats.map((method, index) => (
                <div key={index} className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1 capitalize">
                    {method._id.replace('_', ' ')}
                  </p>
                  <p className="text-2xl font-bold text-gray-900">{method.count}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {formatCurrency(method.total_amount)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recent Transactions */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <TrendingUp size={20} className="text-blue-600" />
                Recent Transactions
              </h2>
              <a
                href="/admin/transactions"
                className="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                View All →
              </a>
            </div>
          </div>

          {recentTransactions.length === 0 ? (
            <div className="p-12 text-center">
              <CreditCard className="mx-auto text-gray-400 mb-4" size={48} />
              <p className="text-gray-600">No transactions yet</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Reference
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Customer
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Method
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {recentTransactions.map((tx) => (
                    <tr key={tx.reference_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {formatDate(tx.created_at)}
                      </td>
                      <td className="px-6 py-4 text-sm font-mono text-gray-600">
                        {tx.reference_id}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {tx.customer_name}
                      </td>
                      <td className="px-6 py-4 text-sm font-semibold text-gray-900">
                        {formatCurrency(tx.amount)}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600 capitalize">
                        {tx.payment_method.replace('_', ' ')}
                      </td>
                      <td className="px-6 py-4">
                        {getStatusBadge(tx.status)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-3 gap-6 mt-8">
          <a
            href="/users"
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow group"
          >
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-blue-50 group-hover:bg-blue-100 transition-colors">
                <Users className="text-blue-600" size={24} />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Manage Users</h3>
                <p className="text-sm text-gray-600">View and edit users</p>
              </div>
            </div>
          </a>

          <a
            href="/payment-settings"
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow group"
          >
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-purple-50 group-hover:bg-purple-100 transition-colors">
                <CreditCard className="text-purple-600" size={24} />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Payment Settings</h3>
                <p className="text-sm text-gray-600">Configure gateways</p>
              </div>
            </div>
          </a>

          <a
            href="/properties"
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow group"
          >
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-green-50 group-hover:bg-green-100 transition-colors">
                <Building2 className="text-green-600" size={24} />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Properties</h3>
                <p className="text-sm text-gray-600">Manage properties</p>
              </div>
            </div>
          </a>
        </div>
      </div>
    </Layout>
  );
};
