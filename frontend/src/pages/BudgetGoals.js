import React, { useState, useEffect } from 'react';
import { Target, TrendingUp, TrendingDown, AlertTriangle, Plus, Edit2, Trash2, DollarSign, Droplets } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

const BudgetGoals = () => {
  const [budgets, setBudgets] = useState([]);
  const [trackingData, setTrackingData] = useState([]);
  const [comparison, setComparison] = useState(null);
  const [selectedPeriod, setSelectedPeriod] = useState('monthly');
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    fetchBudgets();
    fetchTrackingData();
  }, []);

  useEffect(() => {
    if (budgets.length > 0) {
      fetchComparison();
    }
  }, [selectedPeriod, budgets]);

  const fetchBudgets = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/budgets/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setBudgets(data);
      }
    } catch (error) {
      console.error('Error fetching budgets:', error);
    }
  };

  const fetchTrackingData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/budgets/tracking/current`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setTrackingData(data);
      }
    } catch (error) {
      console.error('Error fetching tracking data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchComparison = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/budgets/comparison/${selectedPeriod}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setComparison(data);
      }
    } catch (error) {
      console.error('Error fetching comparison:', error);
      setComparison(null);
    }
  };

  const deleteBudget = async (budgetId) => {
    if (!window.confirm('Are you sure you want to delete this budget?')) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/budgets/${budgetId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        fetchBudgets();
        fetchTrackingData();
      }
    } catch (error) {
      console.error('Error deleting budget:', error);
    }
  };

  const getProgressColor = (percentage) => {
    if (percentage >= 100) return 'bg-red-500';
    if (percentage >= 80) return 'bg-orange-500';
    if (percentage >= 60) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Budget & Usage Goals</h1>
          <p className="text-gray-600">Track your water usage and spending goals</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <Plus size={20} />
          Create Budget
        </button>
      </div>

      {/* Active Budgets */}
      {trackingData.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <Target size={48} className="mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No active budgets</h3>
          <p className="text-gray-600 mb-4">Create a budget to start tracking your usage goals</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Create Your First Budget
          </button>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {trackingData.map(({ budget, tracking }) => (
            <div key={budget.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 capitalize">{budget.period} Budget</h3>
                  <p className="text-sm text-gray-600">
                    {new Date(tracking.period_start).toLocaleDateString()} - {new Date(tracking.period_end).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button className="text-gray-600 hover:text-blue-600">
                    <Edit2 size={18} />
                  </button>
                  <button 
                    onClick={() => deleteBudget(budget.id)}
                    className="text-gray-600 hover:text-red-600"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>

              {/* Budget Limit */}
              <div className="mb-4">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-600">Budget Limit</span>
                  <span className="font-semibold">IDR {budget.limit_amount.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-600">Spent</span>
                  <span className={`font-semibold ${tracking.is_over_budget ? 'text-red-600' : 'text-gray-900'}`}>
                    IDR {tracking.current_spending.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Remaining</span>
                  <span className={`font-semibold ${tracking.remaining_budget < 0 ? 'text-red-600' : 'text-green-600'}`}>
                    IDR {tracking.remaining_budget.toLocaleString()}
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="mb-4">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Progress</span>
                  <span className="font-semibold">{tracking.percentage_used.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full transition-all ${getProgressColor(tracking.percentage_used)}`}
                    style={{ width: `${Math.min(tracking.percentage_used, 100)}%` }}
                  ></div>
                </div>
              </div>

              {/* Usage Stats */}
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Droplets size={16} />
                <span>{tracking.current_usage.toFixed(2)} m³ used</span>
              </div>

              {/* Alert */}
              {tracking.is_over_budget && (
                <div className="mt-4 bg-red-50 border border-red-200 rounded p-3 flex items-start gap-2">
                  <AlertTriangle size={18} className="text-red-600 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-red-800">Over budget by IDR {Math.abs(tracking.remaining_budget).toLocaleString()}</p>
                </div>
              )}
              {!tracking.is_over_budget && tracking.percentage_used >= budget.alert_threshold && (
                <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded p-3 flex items-start gap-2">
                  <AlertTriangle size={18} className="text-yellow-600 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-yellow-800">Approaching limit ({tracking.percentage_used.toFixed(1)}% used)</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Historical Comparison */}
      {comparison && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Historical Comparison</h2>
          
          <div className="mb-4">
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value)}
              className="border border-gray-300 rounded-lg px-4 py-2"
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Current Period */}
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-3">Current {comparison.period}</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Spending</span>
                  <span className="font-semibold">IDR {comparison.current_period.current_spending.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Usage</span>
                  <span className="font-semibold">{comparison.current_period.current_usage.toFixed(2)} m³</span>
                </div>
              </div>
            </div>

            {/* Previous Period */}
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-3">Previous {comparison.period}</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Spending</span>
                  <span className="font-semibold">IDR {comparison.previous_period.current_spending.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Usage</span>
                  <span className="font-semibold">{comparison.previous_period.current_usage.toFixed(2)} m³</span>
                </div>
              </div>
            </div>
          </div>

          {/* Changes */}
          <div className="mt-6 grid md:grid-cols-2 gap-4">
            <div className={`p-4 rounded-lg ${comparison.spending_change > 0 ? 'bg-red-50' : 'bg-green-50'}`}>
              <div className="flex items-center gap-2 mb-1">
                {comparison.spending_change > 0 ? (
                  <TrendingUp className="text-red-600" size={20} />
                ) : (
                  <TrendingDown className="text-green-600" size={20} />
                )}
                <span className="font-semibold text-gray-900">Spending Change</span>
              </div>
              <p className={`text-2xl font-bold ${comparison.spending_change > 0 ? 'text-red-600' : 'text-green-600'}`}>
                {comparison.spending_change > 0 ? '+' : ''}{comparison.spending_change.toFixed(1)}%
              </p>
            </div>

            <div className={`p-4 rounded-lg ${comparison.usage_change > 0 ? 'bg-red-50' : 'bg-green-50'}`}>
              <div className="flex items-center gap-2 mb-1">
                {comparison.usage_change > 0 ? (
                  <TrendingUp className="text-red-600" size={20} />
                ) : (
                  <TrendingDown className="text-green-600" size={20} />
                )}
                <span className="font-semibold text-gray-900">Usage Change</span>
              </div>
              <p className={`text-2xl font-bold ${comparison.usage_change > 0 ? 'text-red-600' : 'text-green-600'}`}>
                {comparison.usage_change > 0 ? '+' : ''}{comparison.usage_change.toFixed(1)}%
              </p>
            </div>
          </div>

          {/* Insights */}
          {comparison.insights && comparison.insights.length > 0 && (
            <div className="mt-6">
              <h3 className="font-semibold text-gray-900 mb-2">Insights</h3>
              <ul className="space-y-2">
                {comparison.insights.map((insight, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-blue-600 mt-1">•</span>
                    <span className="text-gray-700">{insight}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Create Budget Modal */}
      {showCreateModal && (
        <CreateBudgetModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            fetchBudgets();
            fetchTrackingData();
            setShowCreateModal(false);
          }}
        />
      )}
    </div>
  );
};

// Create Budget Modal Component
const CreateBudgetModal = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    period: 'monthly',
    limit_amount: '',
    limit_volume: '',
    alert_threshold: '80'
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      const payload = {
        period: formData.period,
        limit_amount: parseFloat(formData.limit_amount),
        alert_threshold: parseFloat(formData.alert_threshold)
      };

      if (formData.limit_volume) {
        payload.limit_volume = parseFloat(formData.limit_volume);
      }

      const response = await fetch(`${BACKEND_URL}/api/budgets/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to create budget');
      }

      onSuccess();
    } catch (error) {
      console.error('Error creating budget:', error);
      setError(error.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-semibold mb-4">Create Budget Goal</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Period
            </label>
            <select
              value={formData.period}
              onChange={(e) => setFormData({ ...formData, period: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Budget Limit (IDR) *
            </label>
            <input
              type="number"
              value={formData.limit_amount}
              onChange={(e) => setFormData({ ...formData, limit_amount: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., 100000"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Volume Limit (m³) - Optional
            </label>
            <input
              type="number"
              step="0.01"
              value={formData.limit_volume}
              onChange={(e) => setFormData({ ...formData, limit_volume: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., 10.5"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Alert Threshold (%)
            </label>
            <input
              type="number"
              value={formData.alert_threshold}
              onChange={(e) => setFormData({ ...formData, alert_threshold: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              min="1"
              max="100"
              required
            />
            <p className="text-xs text-gray-500 mt-1">You'll receive an alert when you reach this percentage of your budget</p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded p-3 text-sm text-red-800">
              {error}
            </div>
          )}

          <div className="flex gap-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 border border-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300"
            >
              {isSubmitting ? 'Creating...' : 'Create Budget'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default BudgetGoals;
