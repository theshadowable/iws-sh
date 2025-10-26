import React, { useState, useEffect, useCallback } from 'react';
import { Layout } from '@/components/Layout';
import { useWebSocket } from '../hooks/useWebSocket';
import IoTDeviceCard from '../components/IoTDeviceCard';
import {
  Activity, Wifi, WifiOff, RefreshCw, Plus, Settings,
  TrendingUp, Zap, AlertTriangle, CheckCircle
} from 'lucide-react';
import {
  LineChart, Line, AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API = `${BACKEND_URL}/api`;

const IoTMonitoring = () => {
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [deviceMetrics, setDeviceMetrics] = useState({});
  const [historicalData, setHistoricalData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [subscribedDevices, setSubscribedDevices] = useState(new Set());
  
  // CRUD states
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [editingDevice, setEditingDevice] = useState(null);
  const [deletingDevice, setDeletingDevice] = useState(null);
  const [formData, setFormData] = useState({
    device_id: '',
    device_name: '',
    location: '',
    notes: '',
    mac_address: '',
    device_secret: ''
  });

  // WebSocket connection - use useMemo to keep sessionId stable
  const sessionId = React.useMemo(() => 
    `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    [] // Empty deps array means this only runs once
  );
  const { isConnected, lastMessage, subscribe, unsubscribe } = useWebSocket(sessionId);

  // Fetch devices list
  const fetchDevices = useCallback(async (forceRefresh = false) => {
    try {
      if (forceRefresh) {
        setLoading(true);
      }
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/iot/devices/list`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setDevices(data.devices || []);
        
        // Auto-select first device if none selected
        if (data.devices && data.devices.length > 0 && !selectedDevice) {
          setSelectedDevice(data.devices[0].device_id);
        }
        
        if (forceRefresh) {
          console.log('✓ Devices refreshed successfully');
        }
      } else {
        setError('Failed to load devices');
      }
    } catch (err) {
      console.error('Error fetching devices:', err);
      setError('Failed to connect to server');
    } finally {
      if (forceRefresh) {
        setLoading(false);
      }
    }
  }, [selectedDevice]);

  // Fetch device metrics
  const fetchDeviceMetrics = useCallback(async (deviceId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/iot/metrics/realtime/${deviceId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setDeviceMetrics(prev => ({
          ...prev,
          [deviceId]: data.metrics
        }));
      }
    } catch (err) {
      console.error('Error fetching device metrics:', err);
    }
  }, []);

  // Fetch historical data for charts
  const fetchHistoricalData = useCallback(async (deviceId, hours = 24) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/iot/metrics/history/${deviceId}?hours=${hours}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setHistoricalData(data.readings || []);
      }
    } catch (err) {
      console.error('Error fetching historical data:', err);
    }
  }, []);

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      const { type, device_id, data } = lastMessage;

      if (type === 'device_reading') {
        // Update device metrics in real-time
        setDeviceMetrics(prev => {
          const current = prev[device_id] || {};
          return {
            ...prev,
            [device_id]: {
              ...current,
              current_flow_rate: data.flow_rate,
              current_temperature: data.temperature,
              current_pressure: data.pressure,
              battery_level: data.battery_level,
              signal_strength: data.signal_strength,
              last_updated: data.timestamp,
              valve_status: data.valve_status
            }
          };
        });

        // Add to historical data if this is the selected device
        if (device_id === selectedDevice) {
          setHistoricalData(prev => {
            const newData = [...prev, data].slice(-100); // Keep last 100 readings
            return newData;
          });
        }
      } else if (type === 'device_status') {
        // Update device status
        setDevices(prev => prev.map(dev => 
          dev.device_id === device_id 
            ? { ...dev, status: data.status }
            : dev
        ));
      } else if (type === 'alert') {
        // Show alert notification
        console.log('Alert received:', data);
        // You can add toast notification here
      }
    }
  }, [lastMessage, selectedDevice]);

  // Subscribe to device updates
  useEffect(() => {
    if (isConnected && selectedDevice && !subscribedDevices.has(selectedDevice)) {
      subscribe(selectedDevice);
      setSubscribedDevices(prev => new Set([...prev, selectedDevice]));
      fetchDeviceMetrics(selectedDevice);
      fetchHistoricalData(selectedDevice);
    }
  }, [isConnected, selectedDevice, subscribedDevices, subscribe, fetchDeviceMetrics, fetchHistoricalData]);

  // Initial data load
  useEffect(() => {
    fetchDevices();
    
    // Refresh devices every 30 seconds
    const interval = setInterval(() => {
      fetchDevices();
    }, 30000);
    
    return () => clearInterval(interval);
  }, [fetchDevices]);

  // Handle manual refresh
  const handleRefresh = () => {
    fetchDevices(true); // Force refresh with loading state
    if (selectedDevice) {
      fetchDeviceMetrics(selectedDevice);
      fetchHistoricalData(selectedDevice);
    }
  };

  // Handle device selection
  const handleDeviceSelect = (deviceId) => {
    // Unsubscribe from previous device
    if (selectedDevice && selectedDevice !== deviceId) {
      unsubscribe(selectedDevice);
      setSubscribedDevices(prev => {
        const newSet = new Set(prev);
        newSet.delete(selectedDevice);
        return newSet;
      });
    }
    
    setSelectedDevice(deviceId);
  };

  // Prepare chart data
  const prepareChartData = () => {
    return historicalData.map(reading => ({
      time: new Date(reading.timestamp).toLocaleTimeString(),
      flow_rate: reading.flow_rate,
      temperature: reading.temperature,
      pressure: reading.pressure
    })).slice(-50); // Last 50 readings
  };

  const chartData = prepareChartData();

  // CRUD Operations
  const handleAddDevice = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/iot/devices/register`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-Device-Secret': formData.device_secret
        },
        body: JSON.stringify({
          device_id: formData.device_id,
          device_name: formData.device_name,
          location: formData.location,
          notes: formData.notes,
          mac_address: formData.mac_address,
          device_type: 'smart_meter',
          firmware_version: '1.0.0', // Default value
          hardware_version: '1.0'    // Default value
        })
      });

      if (response.ok) {
        setShowAddModal(false);
        setFormData({
          device_id: '',
          device_name: '',
          location: '',
          notes: '',
          mac_address: '',
          device_secret: ''
        });
        fetchDevices(); // Refresh devices list
        alert('Device added successfully!');
      } else {
        const data = await response.json();
        alert(`Failed to add device: ${data.detail || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Error adding device:', err);
      alert('Failed to add device. Please try again.');
    }
  };

  const handleEditDevice = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/iot/devices/${editingDevice.device_id}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          device_name: formData.device_name,
          location: formData.location,
          notes: formData.notes,
          mac_address: formData.mac_address
        })
      });

      if (response.ok) {
        setShowEditModal(false);
        setEditingDevice(null);
        setFormData({
          device_id: '',
          device_name: '',
          location: '',
          notes: '',
          mac_address: '',
          device_secret: ''
        });
        fetchDevices();
        alert('Device updated successfully!');
      } else {
        const data = await response.json();
        alert(`Failed to update device: ${data.detail || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Error updating device:', err);
      alert('Failed to update device. Please try again.');
    }
  };

  const handleDeleteDevice = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/iot/devices/${deletingDevice.device_id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setShowDeleteModal(false);
        setDeletingDevice(null);
        fetchDevices();
        alert('Device deleted successfully!');
      } else {
        const data = await response.json();
        alert(`Failed to delete device: ${data.detail || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Error deleting device:', err);
      alert('Failed to delete device. Please try again.');
    }
  };

  const openEditModal = (device) => {
    setEditingDevice(device);
    setFormData({
      device_id: device.device_id,
      device_name: device.device_name || '',
      location: device.location || '',
      notes: device.notes || '',
      mac_address: device.mac_address || '',
      device_secret: ''
    });
    setShowEditModal(true);
  };

  const openDeleteModal = (device) => {
    setDeletingDevice(device);
    setShowDeleteModal(true);
  };

  if (loading) {
    return (
      <Layout>
        <div className="p-6">
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <RefreshCw className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
              <p className="text-gray-600">Loading Monitoring devices...</p>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="p-6">
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <AlertTriangle className="w-12 h-12 text-red-600 mx-auto mb-4" />
              <p className="text-red-600 text-lg font-semibold mb-2">{error}</p>
              <button
                onClick={() => {
                  setError(null);
                  setLoading(true);
                  fetchDevices();
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Device Monitoring</h1>
            <p className="text-gray-600">Real-time device monitoring and analytics</p>
          </div>
          <div className="flex items-center gap-3">
            {/* Connection Status */}
            <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${isConnected ? 'bg-green-100' : 'bg-red-100'}`}>
              {isConnected ? (
                <>
                  <Wifi className="w-4 h-4 text-green-600" />
                  <span className="text-sm font-medium text-green-700">Connected</span>
                </>
              ) : (
                <>
                  <WifiOff className="w-4 h-4 text-red-600" />
                  <span className="text-sm font-medium text-red-700">Disconnected</span>
                </>
              )}
            </div>
            
            <button
              onClick={handleRefresh}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>
            
            <button 
              onClick={() => setShowAddModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Add Device</span>
            </button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Devices</p>
              <p className="text-2xl font-bold text-gray-900">{devices.length}</p>
            </div>
            <Activity className="w-8 h-8 text-blue-600" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Online Devices</p>
              <p className="text-2xl font-bold text-green-600">
                {devices.filter(d => d.status === 'online').length}
              </p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Active Alerts</p>
              <p className="text-2xl font-bold text-yellow-600">
                {Object.values(deviceMetrics).reduce((sum, m) => sum + (m?.alert_count || 0), 0)}
              </p>
            </div>
            <AlertTriangle className="w-8 h-8 text-yellow-600" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Today's Volume</p>
              <p className="text-2xl font-bold text-blue-600">
                {Object.values(deviceMetrics).reduce((sum, m) => sum + (m?.today_volume || 0), 0).toFixed(2)} L
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-blue-600" />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Device List */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-4">
            <h2 className="text-lg font-semibold mb-4">Devices</h2>
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {devices.map(device => (
                <IoTDeviceCard
                  key={device.device_id}
                  device={device}
                  metrics={deviceMetrics[device.device_id]}
                  onClick={() => handleDeviceSelect(device.device_id)}
                  onEdit={openEditModal}
                  onDelete={openDeleteModal}
                />
              ))}
              
              {devices.length === 0 && (
                <div className="text-center py-8">
                  <Settings className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-600">No devices found</p>
                  <p className="text-sm text-gray-500">Add your first monitoring device to get started</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Charts */}
        <div className="lg:col-span-2">
          {selectedDevice ? (
            <div className="space-y-6">
              {/* Flow Rate Chart */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold mb-4">Flow Rate (L/min)</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area 
                      type="monotone" 
                      dataKey="flow_rate" 
                      stroke="#3b82f6" 
                      fill="#3b82f6" 
                      fillOpacity={0.3}
                      name="Flow Rate"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Temperature & Pressure Chart */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold mb-4">Temperature & Pressure</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip />
                    <Legend />
                    <Line 
                      yAxisId="left"
                      type="monotone" 
                      dataKey="temperature" 
                      stroke="#f97316" 
                      name="Temperature (°C)"
                    />
                    <Line 
                      yAxisId="right"
                      type="monotone" 
                      dataKey="pressure" 
                      stroke="#8b5cf6" 
                      name="Pressure (Bar)"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-md p-12 text-center">
              <Zap className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-xl text-gray-600 mb-2">Select a device to view details</p>
              <p className="text-sm text-gray-500">Real-time monitoring and analytics will appear here</p>
            </div>
          )}
        </div>
      </div>

      {/* Add Device Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6 max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">Add New Monitoring Device</h2>
            <form onSubmit={handleAddDevice}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Device ID (Serial Number) *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.device_id}
                    onChange={(e) => setFormData({...formData, device_id: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., ESP32-001"
                  />
                  <p className="text-xs text-gray-500 mt-1">Unique identifier from device label</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Device Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.device_name}
                    onChange={(e) => setFormData({...formData, device_name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Water Meter - Building A"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Location *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.location}
                    onChange={(e) => setFormData({...formData, location: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Building A - Floor 2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Device Secret (Authentication Key) *
                  </label>
                  <input
                    type="password"
                    required
                    value={formData.device_secret}
                    onChange={(e) => setFormData({...formData, device_secret: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter pre-shared secret key"
                  />
                  <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-xs text-blue-800">
                      <strong>📌 What is Device Secret?</strong><br/>
                      Secret key untuk autentikasi perangkat IoT. Key ini harus sama dengan yang dikonfigurasi di perangkat fisik (ESP32/Arduino). 
                      Contoh: "mySecret123" atau generate random key minimal 16 karakter.
                    </p>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    MAC Address (Optional)
                  </label>
                  <input
                    type="text"
                    value={formData.mac_address}
                    onChange={(e) => setFormData({...formData, mac_address: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="AA:BB:CC:DD:EE:FF"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Notes (Optional)
                  </label>
                  <textarea
                    value={formData.notes}
                    onChange={(e) => setFormData({...formData, notes: e.target.value})}
                    rows="3"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Additional information about this device..."
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowAddModal(false);
                    setFormData({
                      device_id: '',
                      device_name: '',
                      location: '',
                      notes: '',
                      mac_address: '',
                      device_secret: ''
                    });
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Add Device
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Device Modal */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6 max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">Edit Monitoring Device</h2>
            <form onSubmit={handleEditDevice}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Device ID
                  </label>
                  <input
                    type="text"
                    disabled
                    value={formData.device_id}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100"
                  />
                  <p className="text-xs text-gray-500 mt-1">Device ID cannot be changed</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Device Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.device_name}
                    onChange={(e) => setFormData({...formData, device_name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Location *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.location}
                    onChange={(e) => setFormData({...formData, location: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    MAC Address
                  </label>
                  <input
                    type="text"
                    value={formData.mac_address}
                    onChange={(e) => setFormData({...formData, mac_address: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="AA:BB:CC:DD:EE:FF"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Notes (Optional)
                  </label>
                  <textarea
                    value={formData.notes}
                    onChange={(e) => setFormData({...formData, notes: e.target.value})}
                    rows="3"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Additional information about this device..."
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowEditModal(false);
                    setEditingDevice(null);
                    setFormData({
                      device_id: '',
                      device_name: '',
                      location: '',
                      notes: '',
                      mac_address: '',
                      device_secret: ''
                    });
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Update Device
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h2 className="text-2xl font-bold mb-4 text-red-600">Delete Device</h2>
            <p className="text-gray-700 mb-6">
              Are you sure you want to delete device <strong>{deletingDevice?.device_name}</strong> ({deletingDevice?.device_id})? 
              This action cannot be undone and will remove all associated data.
            </p>

            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowDeleteModal(false);
                  setDeletingDevice(null);
                }}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteDevice}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                Delete Device
              </button>
            </div>
          </div>
        </div>
      )}
      </div>
    </Layout>
  );
};

export default IoTMonitoring;
