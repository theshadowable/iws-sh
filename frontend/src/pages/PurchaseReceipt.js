import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  CheckCircle, 
  XCircle, 
  Clock,
  AlertCircle,
  Download,
  Printer,
  ArrowLeft,
  Calendar,
  CreditCard,
  User,
  FileText,
  Droplet
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

export const PurchaseReceipt = () => {
  const { referenceId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [transaction, setTransaction] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTransactionDetails();
  }, [referenceId]);

  const fetchTransactionDetails = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${BACKEND_URL}/api/payments/${referenceId}`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setTransaction(response.data);
    } catch (error) {
      console.error('Failed to fetch transaction:', error);
      toast.error('Failed to load receipt', { id: 'receipt-load-error' });
      navigate('/purchase-history');
    } finally {
      setLoading(false);
    }
  };

  const getStatusConfig = (status) => {
    const configs = {
      paid: {
        icon: CheckCircle,
        color: 'text-green-600',
        bg: 'bg-green-50',
        border: 'border-green-200',
        label: 'Payment Successful'
      },
      pending: {
        icon: Clock,
        color: 'text-yellow-600',
        bg: 'bg-yellow-50',
        border: 'border-yellow-200',
        label: 'Payment Pending'
      },
      failed: {
        icon: XCircle,
        color: 'text-red-600',
        bg: 'bg-red-50',
        border: 'border-red-200',
        label: 'Payment Failed'
      },
      expired: {
        icon: AlertCircle,
        color: 'text-gray-600',
        bg: 'bg-gray-50',
        border: 'border-gray-200',
        label: 'Payment Expired'
      },
      cancelled: {
        icon: XCircle,
        color: 'text-gray-600',
        bg: 'bg-gray-50',
        border: 'border-gray-200',
        label: 'Payment Cancelled'
      }
    };
    return configs[status] || configs.pending;
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

  const handlePrint = () => {
    window.print();
  };

  const handleDownload = () => {
    // Create a simple text receipt
    const receiptText = `
INDOWATER RECEIPT
=====================================
Reference ID: ${transaction.reference_id}
Date: ${formatDate(transaction.created_at)}

CUSTOMER INFORMATION
-------------------------------------
Name: ${transaction.customer_name}
Email: ${transaction.customer_email}
Phone: ${transaction.customer_phone}

TRANSACTION DETAILS
-------------------------------------
Amount: Rp ${transaction.amount.toLocaleString('id-ID')}
Water Volume: ${(transaction.amount / 10000).toFixed(1)} m³
Payment Method: ${getPaymentMethodLabel(transaction.payment_method)}
Status: ${transaction.status.toUpperCase()}

${transaction.paid_at ? `Paid At: ${formatDate(transaction.paid_at)}` : ''}
${transaction.description ? `Description: ${transaction.description}` : ''}

=====================================
Thank you for using IndoWater!
    `.trim();

    const blob = new Blob([receiptText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `receipt-${transaction.reference_id}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Receipt downloaded');
  };

  if (loading) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto p-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 mt-4 text-center">Loading receipt...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (!transaction) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto p-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
            <FileText className="mx-auto text-gray-400 mb-4" size={48} />
            <p className="text-gray-600 text-lg">Receipt not found</p>
          </div>
        </div>
      </Layout>
    );
  }

  const statusConfig = getStatusConfig(transaction.status);
  const StatusIcon = statusConfig.icon;

  return (
    <Layout>
      <div className="max-w-4xl mx-auto p-6">
        {/* Header Actions */}
        <div className="mb-6 flex items-center justify-between print:hidden">
          <button
            onClick={() => navigate('/purchase-history')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft size={20} />
            Back to History
          </button>
          <div className="flex gap-3">
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Download size={18} />
              Download
            </button>
            <button
              onClick={handlePrint}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Printer size={18} />
              Print
            </button>
          </div>
        </div>

        {/* Receipt */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-8 text-center">
            <div className="flex items-center justify-center gap-3 mb-4">
              <Droplet size={32} />
              <h1 className="text-3xl font-bold">IndoWater</h1>
            </div>
            <p className="text-blue-100">Payment Receipt</p>
          </div>

          {/* Status Badge */}
          <div className="p-6 border-b border-gray-200">
            <div className={`flex items-center justify-center gap-3 p-4 rounded-lg ${statusConfig.bg} border ${statusConfig.border}`}>
              <StatusIcon className={statusConfig.color} size={24} />
              <span className={`text-lg font-semibold ${statusConfig.color}`}>
                {statusConfig.label}
              </span>
            </div>
          </div>

          {/* Transaction Details */}
          <div className="p-8 space-y-6">
            {/* Reference ID - More Prominent */}
            <div className="text-center pb-6 border-b-2 border-gray-300">
              <p className="text-sm text-gray-600 mb-2">Transaction Reference Number</p>
              <p className="text-2xl font-mono font-bold text-blue-600 bg-blue-50 py-3 px-4 rounded-lg inline-block">
                {transaction.reference_id}
              </p>
              <p className="text-xs text-gray-500 mt-2">Save this number for your records</p>
            </div>

            {/* Amount */}
            <div className="text-center pb-6 border-b border-gray-200">
              <p className="text-sm text-gray-600 mb-2">Amount Paid</p>
              <p className="text-4xl font-bold text-gray-900 mb-2">
                Rp {transaction.amount.toLocaleString('id-ID')}
              </p>
              <p className="text-gray-600">
                Water Volume: <span className="font-semibold">{(transaction.amount / 10000).toFixed(1)} m³</span>
              </p>
            </div>

            {/* Customer Information - Simplified */}
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-900 text-lg">Customer Information</h3>
              <div className="grid gap-4">
                <div className="flex items-start gap-3">
                  <User className="text-gray-400 mt-0.5" size={20} />
                  <div>
                    <p className="text-sm text-gray-600">Customer Name</p>
                    <p className="font-medium text-gray-900">{transaction.customer_name}</p>
                  </div>
                </div>
                {transaction.meter_id && (
                  <div className="flex items-start gap-3">
                    <Droplet className="text-gray-400 mt-0.5" size={20} />
                    <div>
                      <p className="text-sm text-gray-600">Water Meter ID</p>
                      <p className="font-medium text-gray-900 font-mono">{transaction.meter_id}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Payment Details */}
            <div className="space-y-4 pt-6 border-t border-gray-200">
              <h3 className="font-semibold text-gray-900 text-lg">Payment Details</h3>
              <div className="grid gap-4">
                <div className="flex items-start gap-3">
                  <CreditCard className="text-gray-400 mt-0.5" size={20} />
                  <div>
                    <p className="text-sm text-gray-600">Payment Method</p>
                    <p className="font-medium text-gray-900">
                      {getPaymentMethodLabel(transaction.payment_method)}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Calendar className="text-gray-400 mt-0.5" size={20} />
                  <div>
                    <p className="text-sm text-gray-600">Created At</p>
                    <p className="font-medium text-gray-900">
                      {formatDate(transaction.created_at)}
                    </p>
                  </div>
                </div>
                {transaction.paid_at && (
                  <div className="flex items-start gap-3">
                    <CheckCircle className="text-gray-400 mt-0.5" size={20} />
                    <div>
                      <p className="text-sm text-gray-600">Paid At</p>
                      <p className="font-medium text-gray-900">
                        {formatDate(transaction.paid_at)}
                      </p>
                    </div>
                  </div>
                )}
                {transaction.description && (
                  <div className="flex items-start gap-3">
                    <FileText className="text-gray-400 mt-0.5" size={20} />
                    <div>
                      <p className="text-sm text-gray-600">Description</p>
                      <p className="font-medium text-gray-900">{transaction.description}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="bg-gray-50 p-6 text-center border-t border-gray-200">
            <p className="text-sm text-gray-600">
              Thank you for using IndoWater!
            </p>
            <p className="text-xs text-gray-500 mt-2">
              For support, contact us at support@indowater.com
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
};
