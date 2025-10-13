import React, { useState, useEffect } from 'react';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Droplets, 
  DollarSign, 
  TrendingUp, 
  AlertCircle,
  Gauge,
  Activity,
  Zap,
  Clock,
  Award,
  X,
  ChevronRight,
  Bell
} from 'lucide-react';
import { 
  WaterFlowAnimation, 
  AnimatedCounter, 
  PulsingDot,
  LeakAlertAnimation,
  GaugeAnimation 
} from '@/components/AnimatedComponents';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CustomerDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [tips, setTips] = useState([]);
  const [realTimeData, setRealTimeData] = useState({
    flowRate: 0,
    currentConsumption: 0,
    isFlowing: false
  });
  const [loading, setLoading] = useState(true);
  const [unreadAlerts, setUnreadAlerts] = useState(0);

  useEffect(() => {
    fetchDashboardData();
    fetchAlerts();
    fetchWaterSavingTips();
    
    // Simulate real-time updates every 3 seconds
    const interval = setInterval(() => {
      updateRealTimeData();
    }, 3000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/dashboard/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAlerts = async () => {
    try {
      const token = localStorage.getItem('token');
      const [alertsRes, unreadRes] = await Promise.all([
        axios.get(`${API}/alerts?limit=5`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API}/alerts/unread-count`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      
      setAlerts(alertsRes.data || []);
      setUnreadAlerts(unreadRes.data?.unread_count || 0);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    }
  };

  const fetchWaterSavingTips = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/alerts/tips?viewed=false&limit=3`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTips(response.data || []);
    } catch (error) {
      console.error('Failed to fetch tips:', error);
    }
  };

  const updateRealTimeData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/dashboard/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Simulate real-time flow in L/minute (in production, this would come from WebSocket or polling)
      const isFlowing = Math.random() > 0.3; // 70% chance of flow
      const flowRate = isFlowing ? 0.5 + Math.random() * 9.5 : 0; // 0.5 - 10 L/min
      const currentConsumption = response.data?.total_water_consumed || 0;
      
      setRealTimeData({
        flowRate: flowRate,
        currentConsumption,
        isFlowing
      });
    } catch (error) {
      console.error('Failed to update real-time data:', error);
    }
  };

  const dismissAlert = async (alertId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.patch(
        `${API}/alerts/${alertId}/status`,
        { status: 'dismissed' },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setAlerts(alerts.filter(a => a.id !== alertId));
      setUnreadAlerts(Math.max(0, unreadAlerts - 1));
    } catch (error) {
      console.error('Failed to dismiss alert:', error);
    }
  };

  const markTipViewed = async (tipId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.patch(
        `${API}/alerts/tips/${tipId}/viewed`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setTips(tips.filter(t => t.id !== tipId));
    } catch (error) {
      console.error('Failed to mark tip as viewed:', error);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0
    }).format(value || 0);
  };

  const getAlertIcon = (type) => {
    switch (type) {
      case 'leak_detected':
        return <LeakAlertAnimation />;
      case 'low_balance':
        return <DollarSign className="w-6 h-6 text-yellow-600" />;
      case 'device_tampering':
        return <AlertCircle className="w-6 h-6 text-red-600" />;
      default:
        return <Bell className="w-6 h-6 text-blue-600" />;
    }
  };

  const getAlertColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-50 border-red-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      default:
        return 'bg-blue-50 border-blue-200';
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <motion.div 
            className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full"
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          />
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Welcome back, {user?.full_name}</p>
        </motion.div>

        {/* Real-time Water Consumption - Featured Section */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="bg-gradient-to-br from-blue-500 to-cyan-600 rounded-2xl shadow-lg p-8 text-white overflow-hidden relative"
        >
          {/* Background decoration */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-5 rounded-full -mr-32 -mt-32" />
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-white opacity-5 rounded-full -ml-24 -mb-24" />
          
          <div className="relative z-10">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="p-3 bg-white bg-opacity-20 rounded-xl">
                  <Activity className="w-8 h-8" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold">Real-Time Consumption</h2>
                  <div className="flex items-center space-x-2 mt-1">
                    <PulsingDot color="green" size="sm" />
                    <span className="text-sm opacity-90">Live Monitoring</span>
                  </div>
                </div>
              </div>
              
              <div className="text-right">
                <div className="text-sm opacity-75">Current Flow Rate</div>
                <div className="text-4xl font-bold mt-1">
                  <AnimatedCounter value={realTimeData.flowRate} decimals={1} suffix=" L/min" />
                </div>
              </div>
            </div>

            {/* Water Flow Animation */}
            <div className="mb-6">
              <WaterFlowAnimation 
                isFlowing={realTimeData.isFlowing} 
                flowRate={Math.min((realTimeData.flowRate / 10) * 100, 100)}
              />
            </div>

            {/* Real-time Stats Grid */}
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-white bg-opacity-10 rounded-xl p-4 backdrop-blur-sm">
                <div className="text-sm opacity-75 mb-1">Today's Usage</div>
                <div className="text-2xl font-bold">
                  <AnimatedCounter 
                    value={realTimeData.currentConsumption / 1000} 
                    decimals={2}
                    suffix=" m³"
                  />
                </div>
              </div>
              
              <div className="bg-white bg-opacity-10 rounded-xl p-4 backdrop-blur-sm">
                <div className="text-sm opacity-75 mb-1">Balance</div>
                <div className="text-2xl font-bold">
                  {formatCurrency(stats?.total_balance || 0)}
                </div>
              </div>
              
              <div className="bg-white bg-opacity-10 rounded-xl p-4 backdrop-blur-sm">
                <div className="text-sm opacity-75 mb-1">Devices</div>
                <div className="text-2xl font-bold">
                  {stats?.total_devices || 0} Active
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Balance</p>
                <p className="text-2xl font-bold text-gray-900 mt-2">
                  {formatCurrency(stats?.total_balance || 0)}
                </p>
                <button 
                  onClick={() => navigate('/balance-purchase')}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium mt-2 flex items-center"
                >
                  Top-Up Now <ChevronRight className="w-4 h-4 ml-1" />
                </button>
              </div>
              <div className="p-4 rounded-xl bg-green-500">
                <DollarSign className="h-8 w-8 text-white" />
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Water Consumed</p>
                <p className="text-2xl font-bold text-gray-900 mt-2">
                  {(stats?.total_water_consumed || 0).toFixed(1)} L
                </p>
                <button 
                  onClick={() => navigate('/analytics')}
                  className="text-sm text-cyan-600 hover:text-cyan-700 font-medium mt-2 flex items-center"
                >
                  View Analytics <ChevronRight className="w-4 h-4 ml-1" />
                </button>
              </div>
              <div className="p-4 rounded-xl bg-cyan-500">
                <Droplets className="h-8 w-8 text-white" />
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Devices</p>
                <p className="text-2xl font-bold text-gray-900 mt-2">
                  {stats?.total_devices || 0}
                </p>
                <button 
                  onClick={() => navigate('/my-devices')}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium mt-2 flex items-center"
                >
                  Manage Devices <ChevronRight className="w-4 h-4 ml-1" />
                </button>
              </div>
              <div className="p-4 rounded-xl bg-blue-500">
                <Gauge className="h-8 w-8 text-white" />
              </div>
            </div>
          </motion.div>
        </div>

        {/* Alerts Section */}
        <AnimatePresence>
          {alerts.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-3"
            >
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <AlertCircle className="w-5 h-5 mr-2 text-orange-500" />
                Active Alerts ({unreadAlerts})
              </h3>
              
              {alerts.map((alert, index) => (
                <motion.div
                  key={alert.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: index * 0.1 }}
                  className={`${getAlertColor(alert.severity)} border rounded-xl p-4`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      <div className="mt-1">
                        {getAlertIcon(alert.alert_type)}
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900">{alert.title}</h4>
                        <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                        <p className="text-xs text-gray-500 mt-2">
                          {new Date(alert.created_at).toLocaleString('id-ID')}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => dismissAlert(alert.id)}
                      className="text-gray-400 hover:text-gray-600 transition"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Water Saving Tips */}
        {tips.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl shadow-sm p-6 border border-green-200"
          >
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-2 bg-green-500 rounded-lg">
                <Award className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900">Water Saving Tips</h3>
                <p className="text-sm text-gray-600">Save water and reduce your bills</p>
              </div>
            </div>
            
            <div className="space-y-3">
              {tips.map((tip, index) => (
                <motion.div
                  key={tip.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-white rounded-lg p-4 border border-green-200 hover:shadow-md transition-shadow"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <Zap className="w-4 h-4 text-green-600" />
                        <h4 className="font-semibold text-gray-900">{tip.title}</h4>
                        <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                          Save up to {tip.potential_savings_percentage}%
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">{tip.description}</p>
                    </div>
                    <button
                      onClick={() => markTipViewed(tip.id)}
                      className="ml-4 text-gray-400 hover:text-gray-600"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="bg-white rounded-xl shadow-sm p-6 border border-gray-100"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button 
              onClick={() => navigate('/balance-purchase')}
              className="p-4 border-2 border-dashed border-gray-300 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition text-left group"
            >
              <DollarSign className="h-6 w-6 text-blue-600 mb-2 group-hover:scale-110 transition-transform" />
              <p className="font-medium text-gray-900">Top-Up Balance</p>
              <p className="text-sm text-gray-500">Add credit to your account</p>
            </button>
            
            <button 
              onClick={() => navigate('/analytics')}
              className="p-4 border-2 border-dashed border-gray-300 rounded-xl hover:border-cyan-500 hover:bg-cyan-50 transition text-left group"
            >
              <Droplets className="h-6 w-6 text-cyan-600 mb-2 group-hover:scale-110 transition-transform" />
              <p className="font-medium text-gray-900">View Analytics</p>
              <p className="text-sm text-gray-500">Check your water consumption</p>
            </button>
            
            <button 
              onClick={() => navigate('/purchase-history')}
              className="p-4 border-2 border-dashed border-gray-300 rounded-xl hover:border-purple-500 hover:bg-purple-50 transition text-left group"
            >
              <Clock className="h-6 w-6 text-purple-600 mb-2 group-hover:scale-110 transition-transform" />
              <p className="font-medium text-gray-900">Transaction History</p>
              <p className="text-sm text-gray-500">View past transactions</p>
            </button>
          </div>
        </motion.div>
      </div>
    </Layout>
  );
};

export default CustomerDashboard;
