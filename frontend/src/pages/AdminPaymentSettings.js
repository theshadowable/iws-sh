import React, { useState, useEffect } from 'react';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  Settings, 
  CreditCard,
  Shield,
  CheckCircle,
  XCircle,
  AlertCircle,
  DollarSign
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

export const AdminPaymentSettings = () => {
  const { user } = useAuth();
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeGateway, setActiveGateway] = useState('midtrans');
  const [mode, setMode] = useState('sandbox');

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${BACKEND_URL}/api/admin/payment-settings`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setSettings(response.data);
      setActiveGateway(response.data.active_gateway || 'midtrans');
      setMode(response.data.mode || 'sandbox');
    } catch (error) {
      console.error('Failed to fetch settings:', error);
      toast.error('Failed to load payment settings', { id: 'payment-settings-error' });
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSettings = async () => {
    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `${BACKEND_URL}/api/admin/payment-settings`,
        {
          active_gateway: activeGateway,
          mode: mode
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      toast.success('Payment settings updated successfully!');
      fetchSettings(); // Refresh data
    } catch (error) {
      console.error('Failed to save settings:', error);
      toast.error('Failed to save payment settings');
    } finally {
      setSaving(false);
    }
  };

  const gatewayOptions = [
    {
      id: 'midtrans',
      name: 'Midtrans',
      description: 'All-in-one payment gateway with multiple payment methods',
      features: ['Credit/Debit Card', 'Bank Transfer', 'E-wallet', 'QRIS', 'Retail Stores'],
      logo: '💳'
    },
    {
      id: 'xendit',
      name: 'Xendit',
      description: 'Southeast Asia payment gateway',
      features: ['Virtual Account', 'QRIS', 'E-wallet (OVO, DANA, etc.)', 'Credit Card'],
      logo: '🏦'
    }
  ];

  if (loading) {
    return (
      <Layout>
        <div className="max-w-6xl mx-auto p-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 mt-4 text-center">Loading settings...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-6xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Settings className="text-blue-600" size={32} />
            <h1 className="text-3xl font-bold text-gray-900">
              Payment Gateway Settings
            </h1>
          </div>
          <p className="text-gray-600">
            Configure which payment gateway will be active for customer transactions
          </p>
        </div>

        {/* Alert Banner */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6 flex items-start gap-3">
          <AlertCircle className="text-yellow-600 flex-shrink-0 mt-0.5" size={20} />
          <div className="text-sm text-yellow-800">
            <p className="font-medium mb-1">Important: Single Gateway Mode</p>
            <p>Only one payment gateway can be active at a time to avoid conflicts. Customers will see payment methods supported by the selected gateway.</p>
          </div>
        </div>

        {/* Current Status */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Shield size={20} className="text-blue-600" />
            Current Configuration
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <p className="text-sm text-gray-600 mb-1">Active Gateway</p>
              <p className="text-xl font-semibold text-gray-900">
                {gatewayOptions.find(g => g.id === (settings?.active_gateway || 'midtrans'))?.name}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Mode</p>
              <div className="flex items-center gap-2">
                <span className={`text-xl font-semibold ${settings?.mode === 'live' ? 'text-green-600' : 'text-orange-600'}`}>
                  {settings?.mode === 'live' ? 'Live (Production)' : 'Sandbox (Testing)'}
                </span>
                {settings?.mode === 'live' ? (
                  <CheckCircle className="text-green-600" size={20} />
                ) : (
                  <AlertCircle className="text-orange-600" size={20} />
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Gateway Selection */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Select Active Payment Gateway</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {gatewayOptions.map((gateway) => (
              <div
                key={gateway.id}
                onClick={() => setActiveGateway(gateway.id)}
                className={`
                  p-6 border-2 rounded-lg cursor-pointer transition-all
                  ${activeGateway === gateway.id 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 hover:border-blue-300'
                  }
                `}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">{gateway.logo}</span>
                    <div>
                      <h3 className="font-semibold text-lg text-gray-900">{gateway.name}</h3>
                    </div>
                  </div>
                  {activeGateway === gateway.id && (
                    <CheckCircle className="text-blue-600" size={24} />
                  )}
                </div>
                <p className="text-sm text-gray-600 mb-3">{gateway.description}</p>
                <div>
                  <p className="text-xs font-medium text-gray-700 mb-2">Supported Payment Methods:</p>
                  <div className="flex flex-wrap gap-1">
                    {gateway.features.map((feature, idx) => (
                      <span
                        key={idx}
                        className="text-xs px-2 py-1 bg-white border border-gray-200 rounded"
                      >
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Mode Selection */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Operating Mode</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div
              onClick={() => setMode('sandbox')}
              className={`
                p-6 border-2 rounded-lg cursor-pointer transition-all
                ${mode === 'sandbox' 
                  ? 'border-orange-500 bg-orange-50' 
                  : 'border-gray-200 hover:border-orange-300'
                }
              `}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-lg text-gray-900">Sandbox Mode</h3>
                  <p className="text-sm text-gray-600 mt-1">Testing environment with fake transactions</p>
                </div>
                {mode === 'sandbox' && (
                  <CheckCircle className="text-orange-600" size={24} />
                )}
              </div>
              <ul className="text-sm text-gray-600 space-y-1 mt-3">
                <li>• Use test API keys</li>
                <li>• No real money involved</li>
                <li>• For development & testing</li>
              </ul>
            </div>

            <div
              onClick={() => setMode('live')}
              className={`
                p-6 border-2 rounded-lg cursor-pointer transition-all
                ${mode === 'live' 
                  ? 'border-green-500 bg-green-50' 
                  : 'border-gray-200 hover:border-green-300'
                }
              `}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-lg text-gray-900">Live Mode</h3>
                  <p className="text-sm text-gray-600 mt-1">Production environment with real transactions</p>
                </div>
                {mode === 'live' && (
                  <CheckCircle className="text-green-600" size={24} />
                )}
              </div>
              <ul className="text-sm text-gray-600 space-y-1 mt-3">
                <li>• Use production API keys</li>
                <li>• Real money transactions</li>
                <li>• For live operations</li>
              </ul>
            </div>
          </div>
        </div>

        {/* API Keys Status */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <CreditCard size={20} className="text-blue-600" />
            API Keys Status
          </h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="text-sm font-medium text-gray-700">Midtrans Keys</span>
              <span className="flex items-center gap-2 text-sm text-green-600">
                <CheckCircle size={16} />
                Configured
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="text-sm font-medium text-gray-700">Xendit Keys</span>
              <span className="flex items-center gap-2 text-sm text-green-600">
                <CheckCircle size={16} />
                Configured
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-3">
              Note: API keys are stored securely in environment variables. Update them in your .env file for production use.
            </p>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            onClick={handleSaveSettings}
            disabled={saving}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
          >
            {saving ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Saving...
              </>
            ) : (
              <>
                <Settings size={18} />
                Save Settings
              </>
            )}
          </button>
        </div>
      </div>
    </Layout>
  );
};
