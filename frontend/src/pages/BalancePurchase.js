import React, { useState, useEffect } from 'react';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  Wallet, 
  CreditCard, 
  QrCode, 
  Smartphone,
  Building2,
  ChevronRight,
  Info
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

export const BalancePurchase = () => {
  const { user } = useAuth();
  const [step, setStep] = useState(1);
  const [amount, setAmount] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('');
  const [paymentDetails, setPaymentDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeGateway, setActiveGateway] = useState('midtrans'); // Default gateway
  
  // Xendit specific options
  const [vaBank, setVaBank] = useState('BCA');
  const [ewalletType, setEwalletType] = useState('OVO');

  // Fetch active gateway on component mount
  useEffect(() => {
    fetchActiveGateway();
  }, []);

  const fetchActiveGateway = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${BACKEND_URL}/api/admin/payment-settings`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setActiveGateway(response.data.active_gateway || 'midtrans');
    } catch (error) {
      console.error('Failed to fetch gateway settings:', error);
      // Default to midtrans if fetch fails
      setActiveGateway('midtrans');
    }
  };

  const predefinedAmounts = [
    { value: 50000, label: 'Rp 50.000', water: '5 m³' },
    { value: 100000, label: 'Rp 100.000', water: '10 m³' },
    { value: 250000, label: 'Rp 250.000', water: '25 m³' },
    { value: 500000, label: 'Rp 500.000', water: '50 m³' },
    { value: 1000000, label: 'Rp 1.000.000', water: '100 m³' },
  ];

  // Dynamic payment methods based on active gateway
  const getPaymentMethods = () => {
    if (activeGateway === 'midtrans') {
      return [
        {
          id: 'midtrans',
          name: 'All Payment Methods',
          description: 'Credit/Debit Card, Bank Transfer, E-wallet, QRIS, and more',
          icon: CreditCard,
          color: 'blue',
          note: 'Powered by Midtrans - Choose your preferred method at checkout'
        }
      ];
    } else {
      // Xendit
      return [
        {
          id: 'xendit_va',
          name: 'Virtual Account',
          description: 'BCA, BNI, BRI, Mandiri, Permata',
          icon: Building2,
          color: 'green',
          note: 'Transfer via ATM, mobile banking, or internet banking'
        },
        {
          id: 'xendit_qris',
          name: 'QRIS',
          description: 'Scan QR with any banking app',
          icon: QrCode,
          color: 'purple',
          note: 'Quick and instant payment via QR code'
        },
        {
          id: 'xendit_ewallet',
          name: 'E-wallet',
          description: 'OVO, DANA, LinkAja, ShopeePay',
          icon: Smartphone,
          color: 'orange',
          note: 'Pay using your favorite e-wallet'
        }
      ];
    }
  };

  const paymentMethods = getPaymentMethods();

  const vaBanks = [
    { code: 'BCA', name: 'BCA' },
    { code: 'BNI', name: 'BNI' },
    { code: 'BRI', name: 'BRI' },
    { code: 'MANDIRI', name: 'Mandiri' },
    { code: 'PERMATA', name: 'Permata' }
  ];

  const ewallets = [
    { code: 'OVO', name: 'OVO' },
    { code: 'DANA', name: 'DANA' },
    { code: 'LINKAJA', name: 'LinkAja' },
    { code: 'SHOPEEPAY', name: 'ShopeePay' }
  ];

  const calculateWaterVolume = (rupiah) => {
    return (rupiah / 10000).toFixed(1);
  };

  const handleAmountSelect = (value) => {
    setAmount(value.toString());
    setStep(2);
  };

  const handleCustomAmount = () => {
    if (!amount || parseFloat(amount) < 10000) {
      toast.error('Minimum top-up amount is Rp 10,000');
      return;
    }
    setStep(2);
  };

  const handlePaymentMethodSelect = (methodId) => {
    setPaymentMethod(methodId);
    
    // If Midtrans or QRIS, proceed directly
    if (methodId === 'midtrans' || methodId === 'xendit_qris') {
      handleCreatePayment(methodId);
    } else {
      setStep(3);
    }
  };

  const handleCreatePayment = async (method = paymentMethod) => {
    setLoading(true);
    
    try {
      const token = localStorage.getItem('token');
      const paymentData = {
        customer_id: user.id,
        customer_email: user.email,
        customer_name: user.full_name,
        customer_phone: user.phone || '081234567890',
        amount: parseFloat(amount),
        description: `Water balance top-up ${calculateWaterVolume(amount)} m³`
      };

      let response;

      if (method === 'midtrans') {
        response = await axios.post(
          `${BACKEND_URL}/api/payments/create-midtrans`,
          paymentData,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        
        if (response.data.snap_token) {
          // Redirect to Midtrans Snap page
          window.snap.pay(response.data.snap_token, {
            onSuccess: function(result) {
              toast.success('Payment successful!');
              window.location.href = '/purchase-history';
            },
            onPending: function(result) {
              toast.info('Payment pending...');
              window.location.href = '/purchase-history';
            },
            onError: function(result) {
              toast.error('Payment failed');
            },
            onClose: function() {
              toast.info('Payment window closed');
            }
          });
        }
      } else if (method === 'xendit_va') {
        response = await axios.post(
          `${BACKEND_URL}/api/payments/create-xendit-va`,
          { ...paymentData, bank_code: vaBank },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setPaymentDetails(response.data);
        setStep(4);
      } else if (method === 'xendit_qris') {
        response = await axios.post(
          `${BACKEND_URL}/api/payments/create-xendit-qris`,
          paymentData,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setPaymentDetails(response.data);
        setStep(4);
      } else if (method === 'xendit_ewallet') {
        response = await axios.post(
          `${BACKEND_URL}/api/payments/create-xendit-ewallet`,
          { ...paymentData, ewallet_type: ewalletType },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        
        if (response.data.checkout_url) {
          window.location.href = response.data.checkout_url;
        }
      }

      toast.success('Payment created successfully!');
    } catch (error) {
      console.error('Payment creation error:', error);
      const errorDetail = error.response?.data?.detail || 'Failed to create payment';
      
      // Check for API key errors
      if (errorDetail.includes('INVALID_API_KEY') || errorDetail.includes('API key provided is invalid')) {
        toast.error('Payment gateway not configured. Please contact administrator to set up valid API keys.');
      } else if (errorDetail.includes('Access denied') || errorDetail.includes('invalid')) {
        toast.error('Payment gateway configuration error. Please contact administrator.');
      } else {
        toast.error(errorDetail);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-4xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Top Up Water Balance
          </h1>
          <p className="text-gray-600">
            Add balance to your water meter prepaid account
          </p>
        </div>

        {/* Current Balance Display */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-xl p-6 mb-8 text-white">
          <div className="flex items-center gap-3 mb-2">
            <Wallet size={24} />
            <span className="text-lg font-medium">Current Balance</span>
          </div>
          <div className="text-4xl font-bold">
            {user?.balance ? `${user.balance.toFixed(2)} m³` : '0.00 m³'}
          </div>
          <p className="text-blue-100 mt-2">
            Approximately {user?.balance ? (user.balance * 10000).toLocaleString('id-ID') : '0'} IDR worth of water
          </p>
        </div>

        {/* Step 1: Select Amount */}
        {step === 1 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold mb-4">Select Top-Up Amount</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              {predefinedAmounts.map((item) => (
                <button
                  key={item.value}
                  onClick={() => handleAmountSelect(item.value)}
                  className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all text-left group"
                >
                  <div className="text-lg font-semibold text-gray-900 group-hover:text-blue-600">
                    {item.label}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    = {item.water} water
                  </div>
                </button>
              ))}
            </div>

            <div className="border-t border-gray-200 pt-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Or Enter Custom Amount
              </label>
              <div className="flex gap-3">
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="Minimum Rp 10,000"
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="10000"
                  step="1000"
                />
                <button
                  onClick={handleCustomAmount}
                  disabled={!amount || parseFloat(amount) < 10000}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
                >
                  Continue
                </button>
              </div>
              {amount && parseFloat(amount) >= 10000 && (
                <p className="text-sm text-gray-600 mt-2">
                  You will receive approximately {calculateWaterVolume(amount)} m³ of water
                </p>
              )}
            </div>
          </div>
        )}

        {/* Step 2: Select Payment Method */}
        {step === 2 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold">Select Payment Method</h2>
              <button
                onClick={() => setStep(1)}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                Change Amount
              </button>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <div className="flex items-start gap-3">
                <Info className="text-blue-600 mt-0.5" size={20} />
                <div>
                  <p className="font-medium text-gray-900">
                    Amount: Rp {parseFloat(amount).toLocaleString('id-ID')}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    Water volume: {calculateWaterVolume(amount)} m³
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              {paymentMethods.map((method) => (
                <button
                  key={method.id}
                  onClick={() => handlePaymentMethodSelect(method.id)}
                  disabled={loading}
                  className={`w-full p-5 border-2 rounded-lg hover:border-${method.color}-500 hover:bg-${method.color}-50 transition-all text-left group disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4 flex-1">
                      <div className={`p-3 rounded-lg bg-${method.color}-100 text-${method.color}-600 group-hover:bg-${method.color}-200 flex-shrink-0`}>
                        <method.icon size={24} />
                      </div>
                      <div className="flex-1">
                        <div className="font-semibold text-gray-900 mb-1">{method.name}</div>
                        <div className="text-sm text-gray-600 mb-2">{method.description}</div>
                        {method.note && (
                          <div className="text-xs text-gray-500 italic">{method.note}</div>
                        )}
                      </div>
                    </div>
                    <ChevronRight className="text-gray-400 group-hover:text-gray-600 flex-shrink-0 ml-2" />
                  </div>
                </button>
              ))}
            </div>
            
            {/* Gateway Info */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <p className="text-sm text-gray-600">
                <span className="font-medium">Payment Gateway:</span> {activeGateway === 'midtrans' ? 'Midtrans' : 'Xendit'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Transactions are processed securely through our payment gateway partner
              </p>
            </div>
          </div>
        )}

        {/* Step 3: Additional Options */}
        {step === 3 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold mb-6">Select {paymentMethod === 'xendit_va' ? 'Bank' : 'E-wallet'}</h2>

            {paymentMethod === 'xendit_va' && (
              <div className="space-y-3">
                {vaBanks.map((bank) => (
                  <label
                    key={bank.code}
                    className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      vaBank === bank.code ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name="vaBank"
                      value={bank.code}
                      checked={vaBank === bank.code}
                      onChange={(e) => setVaBank(e.target.value)}
                      className="mr-3"
                    />
                    <span className="font-medium">{bank.name}</span>
                  </label>
                ))}
              </div>
            )}

            {paymentMethod === 'xendit_ewallet' && (
              <div className="space-y-3">
                {ewallets.map((wallet) => (
                  <label
                    key={wallet.code}
                    className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      ewalletType === wallet.code ? 'border-orange-500 bg-orange-50' : 'border-gray-200 hover:border-orange-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name="ewallet"
                      value={wallet.code}
                      checked={ewalletType === wallet.code}
                      onChange={(e) => setEwalletType(e.target.value)}
                      className="mr-3"
                    />
                    <span className="font-medium">{wallet.name}</span>
                  </label>
                ))}
              </div>
            )}

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setStep(2)}
                className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
              >
                Back
              </button>
              <button
                onClick={() => handleCreatePayment()}
                disabled={loading}
                className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {loading ? 'Creating...' : 'Continue'}
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Payment Instructions */}
        {step === 4 && paymentDetails && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold mb-6">Payment Instructions</h2>

            {paymentMethod === 'xendit_va' && (
              <div className="space-y-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-2">Virtual Account Number</p>
                  <p className="text-2xl font-bold text-gray-900 mb-1">
                    {paymentDetails.va_number}
                  </p>
                  <p className="text-sm text-gray-600">
                    Bank: {paymentDetails.bank_code}
                  </p>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Amount to Pay</p>
                  <p className="text-xl font-bold text-gray-900">
                    Rp {parseFloat(amount).toLocaleString('id-ID')}
                  </p>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <p className="text-sm font-medium text-yellow-800 mb-2">Important:</p>
                  <ul className="text-sm text-yellow-700 space-y-1 list-disc list-inside">
                    <li>Transfer exact amount shown above</li>
                    <li>Payment expires in 24 hours</li>
                    <li>Balance will be added automatically after payment</li>
                  </ul>
                </div>

                <button
                  onClick={() => window.location.href = '/purchase-history'}
                  className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  View Payment Status
                </button>
              </div>
            )}

            {paymentMethod === 'xendit_qris' && (
              <div className="space-y-4">
                <div className="flex justify-center">
                  <img
                    src={paymentDetails.qr_code_url || `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${paymentDetails.qr_string}`}
                    alt="QR Code"
                    className="w-64 h-64 border-4 border-gray-200 rounded-lg"
                  />
                </div>

                <div className="bg-gray-50 rounded-lg p-4 text-center">
                  <p className="text-sm text-gray-600 mb-1">Amount to Pay</p>
                  <p className="text-xl font-bold text-gray-900">
                    Rp {parseFloat(amount).toLocaleString('id-ID')}
                  </p>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm font-medium text-blue-800 mb-2">How to pay:</p>
                  <ol className="text-sm text-blue-700 space-y-1 list-decimal list-inside">
                    <li>Open your mobile banking or e-wallet app</li>
                    <li>Select QRIS payment</li>
                    <li>Scan the QR code above</li>
                    <li>Complete the payment</li>
                  </ol>
                </div>

                <button
                  onClick={() => window.location.href = '/purchase-history'}
                  className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  View Payment Status
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Load Midtrans Snap script */}
      {paymentMethod === 'midtrans' && (
        <script
          src="https://app.sandbox.midtrans.com/snap/snap.js"
          data-client-key={process.env.REACT_APP_MIDTRANS_CLIENT_KEY || "Mid-client-SRpKXAjY4_YcEgv1"}
        />
      )}
    </Layout>
  );
};
