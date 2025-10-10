import React, { useState, useEffect } from 'react';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';
import { 
  Users, 
  Building2, 
  Gauge, 
  DollarSign,
  TrendingUp,
  Activity,
  Droplets,
  AlertCircle
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const StatCard = ({ title, value, icon: Icon, color, subtitle }) => (
  <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100" data-testid={`stat-card-${title.toLowerCase().replace(/\s+/g, '-')}`}>
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-600">{title}</p>
        <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
        {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
      </div>
      <div className={`p-4 rounded-xl ${color}`}>
        <Icon className="h-8 w-8 text-white" />
      </div>
    </div>
  </div>
);

export const Dashboard = () => {
  const { user, isAdmin, isTechnician, isCustomer } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0
    }).format(value);
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900" data-testid="dashboard-title">Dashboard</h1>
          <p className="text-gray-600 mt-1">Welcome back, {user?.full_name}</p>
        </div>

        {/* Admin Dashboard */}
        {isAdmin && stats && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard
                title="Total Users"
                value={stats.total_users || 0}
                icon={Users}
                color="bg-blue-500"
              />
              <StatCard
                title="Total Customers"
                value={stats.total_customers || 0}
                icon={Users}
                color="bg-green-500"
              />
              <StatCard
                title="Total Properties"
                value={stats.total_properties || 0}
                icon={Building2}
                color="bg-purple-500"
              />
              <StatCard
                title="Total Devices"
                value={stats.total_devices || 0}
                icon={Gauge}
                color="bg-orange-500"
                subtitle={`${stats.active_devices || 0} active`}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <StatCard
                title="Total Revenue"
                value={formatCurrency(stats.total_revenue || 0)}
                icon={DollarSign}
                color="bg-green-600"
              />
              <StatCard
                title="Total Transactions"
                value={stats.total_transactions || 0}
                icon={TrendingUp}
                color="bg-blue-600"
              />
            </div>
          </>
        )}

        {/* Technician Dashboard */}
        {isTechnician && stats && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard
                title="Total Devices"
                value={stats.total_devices || 0}
                icon={Gauge}
                color="bg-blue-500"
              />
              <StatCard
                title="Active Devices"
                value={stats.active_devices || 0}
                icon={Activity}
                color="bg-green-500"
              />
              <StatCard
                title="Maintenance"
                value={stats.maintenance_devices || 0}
                icon={AlertCircle}
                color="bg-orange-500"
              />
              <StatCard
                title="Faulty Devices"
                value={stats.faulty_devices || 0}
                icon={AlertCircle}
                color="bg-red-500"
              />
            </div>
          </>
        )}

        {/* Customer Dashboard */}
        {isCustomer && stats && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <StatCard
                title="My Devices"
                value={stats.total_devices || 0}
                icon={Gauge}
                color="bg-blue-500"
              />
              <StatCard
                title="Total Balance"
                value={formatCurrency(stats.total_balance || 0)}
                icon={DollarSign}
                color="bg-green-500"
              />
              <StatCard
                title="Water Consumed"
                value={`${(stats.total_water_consumed || 0).toFixed(1)} L`}
                icon={Droplets}
                color="bg-cyan-500"
              />
            </div>

            <StatCard
              title="Total Transactions"
              value={stats.total_transactions || 0}
              icon={TrendingUp}
              color="bg-purple-500"
            />
          </>
        )}

        {/* Quick Actions */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {isAdmin && (
              <>
                <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition text-left">
                  <Users className="h-6 w-6 text-blue-600 mb-2" />
                  <p className="font-medium text-gray-900">Add New User</p>
                  <p className="text-sm text-gray-500">Create admin or technician account</p>
                </button>
                <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition text-left">
                  <Building2 className="h-6 w-6 text-blue-600 mb-2" />
                  <p className="font-medium text-gray-900">Add Property</p>
                  <p className="text-sm text-gray-500">Register new property</p>
                </button>
                <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition text-left">
                  <Gauge className="h-6 w-6 text-blue-600 mb-2" />
                  <p className="font-medium text-gray-900">Register Device</p>
                  <p className="text-sm text-gray-500">Add new water meter</p>
                </button>
              </>
            )}
            {isCustomer && (
              <>
                <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition text-left">
                  <DollarSign className="h-6 w-6 text-blue-600 mb-2" />
                  <p className="font-medium text-gray-900">Top Up Balance</p>
                  <p className="text-sm text-gray-500">Add credit to your account</p>
                </button>
                <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition text-left">
                  <Droplets className="h-6 w-6 text-blue-600 mb-2" />
                  <p className="font-medium text-gray-900">View Usage</p>
                  <p className="text-sm text-gray-500">Check your water consumption</p>
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};