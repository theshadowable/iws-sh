import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API = `${BACKEND_URL}/api`;

const PricingManagement = () => {
  const [pricingTiers, setPricingTiers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showCalculator, setShowCalculator] = useState(false);
  const [editingTier, setEditingTier] = useState(null);
  
  const [formData, setFormData] = useState({
    tier_name: '',
    customer_tier: 'residential',
    pricing_model: 'tiered',
    flat_rate: 0,
    price_ranges: [{ min_volume: 0, max_volume: 10, price_per_unit: 1500, description: '' }],
    admin_fee: 10000,
    minimum_charge: 25000,
    description: '',
    is_active: true
  });

  const [calculator, setCalculator] = useState({
    customer_tier: 'residential',
    usage_volume: 15,
    result: null
  });

  const customerTierOptions = [
    { value: 'residential', label: 'Residential (Rumah Tangga)' },
    { value: 'private_home', label: 'Private Home (Rumah Pribadi)' },
    { value: 'commercial', label: 'Commercial (Komersial)' },
    { value: 'industrial', label: 'Industrial (Industri)' }
  ];

  useEffect(() => {
    fetchPricingTiers();
  }, []);

  const fetchPricingTiers = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/pricing/tiers`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPricingTiers(data);
      } else {
        toast.error('Failed to load pricing tiers');
      }
    } catch (error) {
      console.error('Error fetching pricing tiers:', error);
      toast.error('Error loading pricing tiers');
    } finally {
      setLoading(false);
    }
  };

  const handleSeedDefaults = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/pricing/seed-defaults`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        toast.success(data.message);
        fetchPricingTiers();
      } else {
        toast.error('Failed to seed default pricing tiers');
      }
    } catch (error) {
      console.error('Error seeding defaults:', error);
      toast.error('Error seeding defaults');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('token');
      const url = editingTier 
        ? `${API}/pricing/tiers/${editingTier.id}`
        : `${API}/pricing/tiers`;
      
      const method = editingTier ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        toast.success(editingTier ? 'Pricing tier updated' : 'Pricing tier created');
        setShowModal(false);
        setEditingTier(null);
        resetForm();
        fetchPricingTiers();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to save pricing tier');
      }
    } catch (error) {
      console.error('Error saving pricing tier:', error);
      toast.error('Error saving pricing tier');
    }
  };

  const handleDelete = async (tierId) => {
    if (!window.confirm('Are you sure you want to delete this pricing tier?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/pricing/tiers/${tierId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        toast.success('Pricing tier deleted');
        fetchPricingTiers();
      } else {
        toast.error('Failed to delete pricing tier');
      }
    } catch (error) {
      console.error('Error deleting pricing tier:', error);
      toast.error('Error deleting pricing tier');
    }
  };

  const handleEdit = (tier) => {
    setEditingTier(tier);
    setFormData({
      tier_name: tier.tier_name,
      customer_tier: tier.customer_tier,
      pricing_model: tier.pricing_model,
      flat_rate: tier.flat_rate || 0,
      price_ranges: tier.price_ranges || [{ min_volume: 0, max_volume: 10, price_per_unit: 1500, description: '' }],
      admin_fee: tier.admin_fee,
      minimum_charge: tier.minimum_charge,
      description: tier.description || '',
      is_active: tier.is_active
    });
    setShowModal(true);
  };

  const resetForm = () => {
    setFormData({
      tier_name: '',
      customer_tier: 'residential',
      pricing_model: 'tiered',
      flat_rate: 0,
      price_ranges: [{ min_volume: 0, max_volume: 10, price_per_unit: 1500, description: '' }],
      admin_fee: 10000,
      minimum_charge: 25000,
      description: '',
      is_active: true
    });
  };

  const addPriceRange = () => {
    const lastRange = formData.price_ranges[formData.price_ranges.length - 1];
    const newMin = lastRange.max_volume || lastRange.min_volume + 10;
    setFormData({
      ...formData,
      price_ranges: [
        ...formData.price_ranges,
        { min_volume: newMin, max_volume: newMin + 10, price_per_unit: 2000, description: '' }
      ]
    });
  };

  const removePriceRange = (index) => {
    const newRanges = formData.price_ranges.filter((_, i) => i !== index);
    setFormData({ ...formData, price_ranges: newRanges });
  };

  const updatePriceRange = (index, field, value) => {
    const newRanges = [...formData.price_ranges];
    newRanges[index][field] = field === 'description' ? value : parseFloat(value) || 0;
    setFormData({ ...formData, price_ranges: newRanges });
  };

  const handleCalculate = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/pricing/calculate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          customer_tier: calculator.customer_tier,
          usage_volume: calculator.usage_volume
        })
      });

      if (response.ok) {
        const result = await response.json();
        setCalculator({ ...calculator, result });
      } else {
        toast.error('Failed to calculate bill');
      }
    } catch (error) {
      console.error('Error calculating bill:', error);
      toast.error('Error calculating bill');
    }
  };

  const getTierColor = (tier) => {
    const colors = {
      residential: 'bg-green-100 text-green-800',
      private_home: 'bg-blue-100 text-blue-800',
      commercial: 'bg-purple-100 text-purple-800',
      industrial: 'bg-orange-100 text-orange-800'
    };
    return colors[tier] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Pricing Management</h1>
          <p className="text-gray-600">Manage multi-tier water pricing</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowCalculator(true)}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            Bill Calculator
          </button>
          {pricingTiers.length === 0 && (
            <button
              onClick={handleSeedDefaults}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Seed Default Tiers
            </button>
          )}
          <button
            onClick={() => {
              setEditingTier(null);
              resetForm();
              setShowModal(true);
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Pricing Tier
          </button>
        </div>
      </div>

      {/* Pricing Tiers Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : pricingTiers.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="mt-2 text-gray-500">No pricing tiers found</p>
          <button
            onClick={handleSeedDefaults}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Seed Default Pricing Tiers
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {pricingTiers.map((tier) => (
            <div key={tier.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">{tier.tier_name}</h3>
                  <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold mt-2 ${getTierColor(tier.customer_tier)}`}>
                    {tier.customer_tier.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEdit(tier)}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => handleDelete(tier.id)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>

              <p className="text-sm text-gray-600 mb-4">{tier.description}</p>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Model:</span>
                  <span className="font-medium capitalize">{tier.pricing_model.replace('_', ' ')}</span>
                </div>

                {tier.pricing_model === 'flat_rate' ? (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Rate:</span>
                    <span className="font-medium">Rp {tier.flat_rate?.toLocaleString('id-ID')}/m³</span>
                  </div>
                ) : (
                  <div className="mt-2">
                    <p className="text-gray-600 mb-1">Price Ranges:</p>
                    {tier.price_ranges?.map((range, idx) => (
                      <div key={idx} className="flex justify-between text-xs bg-gray-50 p-2 rounded mb-1">
                        <span>{range.description || `${range.min_volume}-${range.max_volume || '∞'} m³`}</span>
                        <span className="font-medium">Rp {range.price_per_unit.toLocaleString('id-ID')}</span>
                      </div>
                    ))}
                  </div>
                )}

                <div className="flex justify-between">
                  <span className="text-gray-600">Admin Fee:</span>
                  <span className="font-medium">Rp {tier.admin_fee.toLocaleString('id-ID')}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Min. Charge:</span>
                  <span className="font-medium">Rp {tier.minimum_charge.toLocaleString('id-ID')}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <span className={`font-medium ${tier.is_active ? 'text-green-600' : 'text-red-600'}`}>
                    {tier.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
          <div className="bg-white rounded-lg p-6 max-w-3xl w-full m-4 max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">
              {editingTier ? 'Edit Pricing Tier' : 'Add New Pricing Tier'}
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tier Name</label>
                  <input
                    type="text"
                    required
                    value={formData.tier_name}
                    onChange={(e) => setFormData({...formData, tier_name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Customer Tier</label>
                  <select
                    value={formData.customer_tier}
                    onChange={(e) => setFormData({...formData, customer_tier: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    {customerTierOptions.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Pricing Model</label>
                  <select
                    value={formData.pricing_model}
                    onChange={(e) => setFormData({...formData, pricing_model: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="flat_rate">Flat Rate</option>
                    <option value="tiered">Tiered</option>
                    <option value="progressive">Progressive</option>
                  </select>
                </div>

                {formData.pricing_model === 'flat_rate' ? (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Flat Rate (IDR/m³)</label>
                    <input
                      type="number"
                      required
                      value={formData.flat_rate}
                      onChange={(e) => setFormData({...formData, flat_rate: parseFloat(e.target.value)})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                ) : null}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Admin Fee (IDR)</label>
                  <input
                    type="number"
                    required
                    value={formData.admin_fee}
                    onChange={(e) => setFormData({...formData, admin_fee: parseFloat(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Minimum Charge (IDR)</label>
                  <input
                    type="number"
                    required
                    value={formData.minimum_charge}
                    onChange={(e) => setFormData({...formData, minimum_charge: parseFloat(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              {formData.pricing_model !== 'flat_rate' && (
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label className="block text-sm font-medium text-gray-700">Price Ranges</label>
                    <button
                      type="button"
                      onClick={addPriceRange}
                      className="text-sm text-blue-600 hover:text-blue-800"
                    >
                      + Add Range
                    </button>
                  </div>
                  {formData.price_ranges.map((range, index) => (
                    <div key={index} className="grid grid-cols-5 gap-2 mb-2">
                      <input
                        type="number"
                        placeholder="Min m³"
                        value={range.min_volume}
                        onChange={(e) => updatePriceRange(index, 'min_volume', e.target.value)}
                        className="px-3 py-2 border border-gray-300 rounded-lg"
                      />
                      <input
                        type="number"
                        placeholder="Max m³"
                        value={range.max_volume || ''}
                        onChange={(e) => updatePriceRange(index, 'max_volume', e.target.value)}
                        className="px-3 py-2 border border-gray-300 rounded-lg"
                      />
                      <input
                        type="number"
                        placeholder="Price/m³"
                        value={range.price_per_unit}
                        onChange={(e) => updatePriceRange(index, 'price_per_unit', e.target.value)}
                        className="px-3 py-2 border border-gray-300 rounded-lg"
                      />
                      <input
                        type="text"
                        placeholder="Description"
                        value={range.description}
                        onChange={(e) => updatePriceRange(index, 'description', e.target.value)}
                        className="px-3 py-2 border border-gray-300 rounded-lg"
                      />
                      <button
                        type="button"
                        onClick={() => removePriceRange(index)}
                        className="text-red-600 hover:text-red-800"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <label className="ml-2 text-sm text-gray-700">Active</label>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setEditingTier(null);
                    resetForm();
                  }}
                  className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  {editingTier ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Bill Calculator Modal */}
      {showCalculator && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full m-4">
            <h2 className="text-2xl font-bold mb-4">Bill Calculator</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Customer Tier</label>
                <select
                  value={calculator.customer_tier}
                  onChange={(e) => setCalculator({...calculator, customer_tier: e.target.value, result: null})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  {customerTierOptions.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Usage Volume (m³)</label>
                <input
                  type="number"
                  step="0.01"
                  value={calculator.usage_volume}
                  onChange={(e) => setCalculator({...calculator, usage_volume: parseFloat(e.target.value), result: null})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <button
                onClick={handleCalculate}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Calculate Bill
              </button>

              {calculator.result && (
                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-bold text-lg mb-3">{calculator.result.pricing_tier_name}</h3>
                  
                  <div className="space-y-2 text-sm mb-4">
                    {calculator.result.breakdown.map((item, idx) => (
                      <div key={idx} className="flex justify-between">
                        <span className="text-gray-600">{item.range} ({item.volume} m³ × Rp {item.rate.toLocaleString('id-ID')})</span>
                        <span className="font-medium">Rp {item.subtotal.toLocaleString('id-ID')}</span>
                      </div>
                    ))}
                  </div>

                  <div className="border-t pt-3 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Water Charge:</span>
                      <span className="font-medium">Rp {calculator.result.water_charge.toLocaleString('id-ID')}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Admin Fee:</span>
                      <span className="font-medium">Rp {calculator.result.admin_fee.toLocaleString('id-ID')}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Tax (11%):</span>
                      <span className="font-medium">Rp {calculator.result.tax.toLocaleString('id-ID')}</span>
                    </div>
                    <div className="flex justify-between text-lg font-bold border-t pt-2">
                      <span>Total:</span>
                      <span className="text-blue-600">Rp {calculator.result.total_amount.toLocaleString('id-ID')}</span>
                    </div>
                  </div>
                </div>
              )}

              <button
                onClick={() => setShowCalculator(false)}
                className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PricingManagement;
