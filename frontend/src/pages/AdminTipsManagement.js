import React, { useState, useEffect } from 'react';
import {
  Search, Filter, Lightbulb, Plus, Edit, Trash2, Eye, RefreshCw,
  TrendingUp, Heart, CheckCircle, XCircle, BookOpen, Target
} from 'lucide-react';
import { Layout } from '../components/Layout';
import toast from 'react-hot-toast';

const AdminTipsManagement = () => {
  const [tips, setTips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [difficultyFilter, setDifficultyFilter] = useState('all');
  const [stats, setStats] = useState({
    total: 0,
    published: 0,
    draft: 0,
    totalViews: 0,
    totalImplementations: 0
  });

  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [selectedTip, setSelectedTip] = useState(null);

  // Form states - field names match backend API
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'general_savings',
    difficulty_level: 'easy',
    potential_savings_percentage: 0,
    implementation_time: '5 menit',
    implementation_steps: [],
    benefits: [],
    required_tools: [],
    tags: []
  });

  const [newStep, setNewStep] = useState('');
  const [newBenefit, setNewBenefit] = useState('');
  const [newTool, setNewTool] = useState('');

  // Use relative URLs to avoid mixed content issues - frontend and backend are on same domain
  const API_BASE = '/api';

  useEffect(() => {
    fetchTips();
    calculateStats();
  }, [categoryFilter, difficultyFilter]);

  const fetchTips = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      // Important: Use trailing slash for FastAPI routes
      let url = `${API_BASE}/tips/?limit=100`;

      if (categoryFilter !== 'all') url += `&category=${categoryFilter}`;
      if (difficultyFilter !== 'all') url += `&difficulty=${difficultyFilter}`;

      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setTips(data.tips || []);
      } else {
        console.error('Failed to fetch tips:', response.status);
        // Don't show error toast on empty data (404)
        if (response.status !== 404) {
          toast.error('Failed to load tips');
        }
      }
    } catch (error) {
      console.error('Error fetching tips:', error);
      // Only show toast for network errors, not HTTP errors (already handled above)
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = () => {
    const published = tips.filter(t => t.status === 'published').length;
    const draft = tips.filter(t => t.status === 'draft').length;
    const totalViews = tips.reduce((sum, t) => sum + (t.view_count || 0), 0);
    const totalImplementations = tips.reduce((sum, t) => sum + (t.implementation_count || 0), 0);

    setStats({
      total: tips.length,
      published,
      draft,
      totalViews,
      totalImplementations
    });
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      category: 'general_savings',
      difficulty_level: 'easy',
      potential_savings_percentage: 0,
      implementation_time: '5 menit',
      implementation_steps: [],
      benefits: [],
      required_tools: [],
      tags: []
    });
  };

  const handleCreateTip = async () => {
    if (!formData.title || !formData.description) {
      toast.error('Mohon isi semua field yang wajib');
      return;
    }

    // Validate title length (backend requires min 5 chars)
    if (formData.title.length < 5) {
      toast.error('Judul harus minimal 5 karakter');
      return;
    }

    // Validate description length (backend requires min 20 chars)
    if (formData.description.length < 20) {
      toast.error('Deskripsi harus minimal 20 karakter');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/tips/admin/create`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        toast.success('Tip created successfully');
        setShowCreateModal(false);
        resetForm();
        fetchTips();
      } else {
        const error = await response.json();
        // Handle validation errors (array of objects)
        if (Array.isArray(error.detail)) {
          const errorMessages = error.detail.map(err => err.msg).join(', ');
          toast.error(`Validation error: ${errorMessages}`);
        } else if (typeof error.detail === 'string') {
          toast.error(error.detail);
        } else {
          toast.error('Failed to create tip');
        }
      }
    } catch (error) {
      console.error('Error creating tip:', error);
      toast.error('Error creating tip');
    }
  };

  const handleEditTip = async () => {
    if (!formData.title || !formData.description) {
      toast.error('Mohon isi semua field yang wajib');
      return;
    }

    // Validate title length (backend requires min 5 chars)
    if (formData.title.length < 5) {
      toast.error('Judul harus minimal 5 karakter');
      return;
    }

    // Validate description length (backend requires min 20 chars)
    if (formData.description.length < 20) {
      toast.error('Deskripsi harus minimal 20 karakter');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/tips/admin/${selectedTip.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        toast.success('Tip updated successfully');
        setShowEditModal(false);
        setSelectedTip(null);
        resetForm();
        fetchTips();
      } else {
        const error = await response.json();
        // Handle validation errors (array of objects)
        if (Array.isArray(error.detail)) {
          const errorMessages = error.detail.map(err => err.msg).join(', ');
          toast.error(`Validation error: ${errorMessages}`);
        } else if (typeof error.detail === 'string') {
          toast.error(error.detail);
        } else {
          toast.error('Failed to update tip');
        }
      }
    } catch (error) {
      console.error('Error updating tip:', error);
      toast.error('Error updating tip');
    }
  };

  const handleDeleteTip = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/tips/admin/${selectedTip.id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        toast.success('Tip deleted successfully');
        setShowDeleteModal(false);
        setSelectedTip(null);
        fetchTips();
      } else {
        toast.error('Failed to delete tip');
      }
    } catch (error) {
      console.error('Error deleting tip:', error);
      toast.error('Error deleting tip');
    }
  };

  const openEditModal = (tip) => {
    setSelectedTip(tip);
    setFormData({
      title: tip.title,
      description: tip.description,
      category: tip.category,
      difficulty_level: tip.difficulty_level,
      potential_savings_percentage: tip.potential_savings_percentage || 0,
      implementation_time: tip.implementation_time || '5 menit',
      implementation_steps: tip.implementation_steps || [],
      benefits: tip.benefits || [],
      required_tools: tip.required_tools || [],
      tags: tip.tags || []
    });
    setShowEditModal(true);
  };

  const addStep = () => {
    if (newStep.trim()) {
      setFormData({ ...formData, implementation_steps: [...formData.implementation_steps, newStep.trim()] });
      setNewStep('');
    }
  };

  const removeStep = (index) => {
    setFormData({ ...formData, implementation_steps: formData.implementation_steps.filter((_, i) => i !== index) });
  };

  const addBenefit = () => {
    if (newBenefit.trim()) {
      setFormData({ ...formData, benefits: [...formData.benefits, newBenefit.trim()] });
      setNewBenefit('');
    }
  };

  const removeBenefit = (index) => {
    setFormData({ ...formData, benefits: formData.benefits.filter((_, i) => i !== index) });
  };

  const addTool = () => {
    if (newTool.trim()) {
      setFormData({ ...formData, required_tools: [...formData.required_tools, newTool.trim()] });
      setNewTool('');
    }
  };

  const removeTool = (index) => {
    setFormData({ ...formData, required_tools: formData.required_tools.filter((_, i) => i !== index) });
  };

  const getCategoryLabel = (category) => {
    const labels = {
      'general_savings': 'Penghematan Umum',
      'leak_prevention': 'Pencegahan Kebocoran',
      'best_practices': 'Praktik Terbaik',
      'saran_penghematan_prabayar': 'Saran Penghematan Prabayar'
    };
    return labels[category] || category;
  };

  const getDifficultyBadge = (difficulty) => {
    const badges = {
      'easy': { bg: 'bg-green-100', text: 'text-green-700', label: 'Easy' },
      'medium': { bg: 'bg-yellow-100', text: 'text-yellow-700', label: 'Medium' },
      'hard': { bg: 'bg-red-100', text: 'text-red-700', label: 'Hard' }
    };
    return badges[difficulty] || badges['easy'];
  };

  const filteredTips = tips.filter(tip =>
    tip.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    tip.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Layout>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Water Conservation Tips Management</h1>
            <p className="text-gray-600 mt-1">Create and manage water saving tips for users</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={fetchTips}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center gap-2"
            >
              <RefreshCw className="w-5 h-5" />
              Refresh
            </button>
            <button
              onClick={() => {
                resetForm();
                setShowCreateModal(true);
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              Create New Tip
            </button>
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Tips</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
              <Lightbulb className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Published</p>
                <p className="text-2xl font-bold text-green-600">{stats.published}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Draft</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.draft}</p>
              </div>
              <BookOpen className="w-8 h-8 text-yellow-600" />
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Views</p>
                <p className="text-2xl font-bold text-purple-600">{stats.totalViews}</p>
              </div>
              <Eye className="w-8 h-8 text-purple-600" />
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Implementations</p>
                <p className="text-2xl font-bold text-orange-600">{stats.totalImplementations}</p>
              </div>
              <Target className="w-8 h-8 text-orange-600" />
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white p-4 rounded-lg shadow mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search tips..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Category Filter */}
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Categories</option>
              <option value="saving_water">Saving Water</option>
              <option value="leak_prevention">Leak Prevention</option>
              <option value="conservation">Conservation</option>
              <option value="maintenance">Maintenance</option>
              <option value="efficiency">Efficiency</option>
            </select>

            {/* Difficulty Filter */}
            <select
              value={difficultyFilter}
              onChange={(e) => setDifficultyFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Difficulties</option>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
        </div>

        {/* Tips Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {loading ? (
            <div className="p-8 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-gray-600">Loading tips...</p>
            </div>
          ) : filteredTips.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <Lightbulb className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <p>No tips found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Difficulty</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Savings</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Engagement</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredTips.map((tip) => {
                    const DifficultyBadge = getDifficultyBadge(tip.difficulty_level);

                    return (
                      <tr key={tip.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div className="text-sm font-medium text-gray-900 max-w-xs">
                            {tip.title}
                          </div>
                          <div className="text-xs text-gray-500 mt-1 truncate max-w-xs">
                            {tip.description}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm text-gray-600">
                            {getCategoryLabel(tip.category)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${DifficultyBadge.bg} ${DifficultyBadge.text}`}>
                            {DifficultyBadge.label}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {tip.potential_savings_percentage || 0}%
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            tip.is_active 
                              ? 'bg-green-100 text-green-700' 
                              : 'bg-gray-100 text-gray-700'
                          }`}>
                            {tip.is_active ? 'Aktif' : 'Nonaktif'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center gap-3 text-sm text-gray-600">
                            <div className="flex items-center gap-1">
                              <Eye className="w-4 h-4" />
                              {tip.view_count || 0}
                            </div>
                            <div className="flex items-center gap-1">
                              <Heart className="w-4 h-4" />
                              {tip.like_count || 0}
                            </div>
                            <div className="flex items-center gap-1">
                              <CheckCircle className="w-4 h-4" />
                              {tip.implementation_count || 0}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex gap-2">
                            <button
                              onClick={() => {
                                setSelectedTip(tip);
                                setShowPreviewModal(true);
                              }}
                              className="text-purple-600 hover:text-purple-900 transition-colors"
                              title="Preview"
                            >
                              <Eye className="w-5 h-5" />
                            </button>
                            <button
                              onClick={() => openEditModal(tip)}
                              className="text-blue-600 hover:text-blue-900 transition-colors"
                              title="Edit"
                            >
                              <Edit className="w-5 h-5" />
                            </button>
                            <button
                              onClick={() => {
                                setSelectedTip(tip);
                                setShowDeleteModal(true);
                              }}
                              className="text-red-600 hover:text-red-900 transition-colors"
                              title="Delete"
                            >
                              <Trash2 className="w-5 h-5" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Create/Edit Modal */}
        {(showCreateModal || showEditModal) && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
            <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full my-8">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-bold text-gray-900">
                  {showCreateModal ? 'Create New Tip' : 'Edit Tip'}
                </h3>
              </div>

              <div className="p-6 space-y-4 max-h-[70vh] overflow-y-auto">
                {/* Title */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Judul <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Masukkan judul tips..."
                  />
                  <p className="mt-1 text-xs text-gray-500">Minimal 5 karakter</p>
                </div>

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Deskripsi <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    rows={4}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Masukkan deskripsi lengkap..."
                  />
                  <p className="mt-1 text-xs text-gray-500">Minimal 20 karakter</p>
                </div>

                {/* Category and Difficulty */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Kategori
                    </label>
                    <select
                      value={formData.category}
                      onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="general_savings">Penghematan Umum</option>
                      <option value="leak_prevention">Pencegahan Kebocoran</option>
                      <option value="best_practices">Praktik Terbaik</option>
                      <option value="saran_penghematan_prabayar">Saran Penghematan Prabayar</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Tingkat Kesulitan
                    </label>
                    <select
                      value={formData.difficulty_level}
                      onChange={(e) => setFormData({ ...formData, difficulty_level: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="easy">Mudah</option>
                      <option value="medium">Sedang</option>
                      <option value="hard">Sulit</option>
                    </select>
                  </div>
                </div>

                {/* Estimated Savings and Time */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Estimasi Penghematan (%)
                    </label>
                    <input
                      type="number"
                      value={formData.potential_savings_percentage}
                      onChange={(e) => setFormData({ ...formData, potential_savings_percentage: parseInt(e.target.value) || 0 })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      min="0"
                      max="100"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Waktu Implementasi
                    </label>
                    <input
                      type="text"
                      value={formData.implementation_time}
                      onChange={(e) => setFormData({ ...formData, implementation_time: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g., 5 menit, 1 jam"
                    />
                  </div>
                </div>

                {/* Steps */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Langkah Implementasi
                  </label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={newStep}
                      onChange={(e) => setNewStep(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && addStep()}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Tambah langkah..."
                    />
                    <button
                      onClick={addStep}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      <Plus className="w-5 h-5" />
                    </button>
                  </div>
                  <div className="space-y-2">
                    {formData.implementation_steps.map((step, index) => (
                      <div key={index} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                        <span className="text-sm text-gray-700 flex-1">{index + 1}. {step}</span>
                        <button
                          onClick={() => removeStep(index)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <XCircle className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Benefits */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Manfaat
                  </label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={newBenefit}
                      onChange={(e) => setNewBenefit(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && addBenefit()}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Add a benefit..."
                    />
                    <button
                      onClick={addBenefit}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      <Plus className="w-5 h-5" />
                    </button>
                  </div>
                  <div className="space-y-2">
                    {formData.benefits.map((benefit, index) => (
                      <div key={index} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                        <span className="text-sm text-gray-700 flex-1">{benefit}</span>
                        <button
                          onClick={() => removeBenefit(index)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <XCircle className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Required Tools */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Required Tools
                  </label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={newTool}
                      onChange={(e) => setNewTool(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && addTool()}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Add a tool..."
                    />
                    <button
                      onClick={addTool}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      <Plus className="w-5 h-5" />
                    </button>
                  </div>
                  <div className="space-y-2">
                    {formData.required_tools.map((tool, index) => (
                      <div key={index} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                        <span className="text-sm text-gray-700 flex-1">{tool}</span>
                        <button
                          onClick={() => removeTool(index)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <XCircle className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Status */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Status
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="published">Published</option>
                    <option value="draft">Draft</option>
                  </select>
                </div>
              </div>

              <div className="px-6 py-4 bg-gray-50 flex gap-3 justify-end">
                <button
                  onClick={() => {
                    if (showCreateModal) setShowCreateModal(false);
                    if (showEditModal) setShowEditModal(false);
                    resetForm();
                    setSelectedTip(null);
                  }}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={showCreateModal ? handleCreateTip : handleEditTip}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  {showCreateModal ? 'Create Tip' : 'Update Tip'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Preview Modal */}
        {showPreviewModal && selectedTip && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-bold text-gray-900">{selectedTip.title}</h3>
                  <button
                    onClick={() => setShowPreviewModal(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <XCircle className="w-6 h-6" />
                  </button>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                <div>
                  <p className="text-gray-700">{selectedTip.description}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <p className="text-sm text-gray-600">Category</p>
                    <p className="font-medium text-gray-900">{getCategoryLabel(selectedTip.category)}</p>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <p className="text-sm text-gray-600">Tingkat Kesulitan</p>
                    <p className="font-medium text-gray-900">{selectedTip.difficulty_level}</p>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <p className="text-sm text-gray-600">Estimasi Penghematan</p>
                    <p className="font-medium text-gray-900">{selectedTip.potential_savings_percentage || 0}%</p>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <p className="text-sm text-gray-600">Waktu Implementasi</p>
                    <p className="font-medium text-gray-900">{selectedTip.implementation_time}</p>
                  </div>
                </div>

                {selectedTip.implementation_steps && selectedTip.implementation_steps.length > 0 && (
                  <div>
                    <h4 className="font-bold text-gray-900 mb-3">Langkah Implementasi</h4>
                    <ol className="space-y-2">
                      {selectedTip.implementation_steps.map((step, index) => (
                        <li key={index} className="flex gap-3">
                          <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm">
                            {index + 1}
                          </span>
                          <span className="text-gray-700">{step}</span>
                        </li>
                      ))}
                    </ol>
                  </div>
                )}

                {selectedTip.benefits && selectedTip.benefits.length > 0 && (
                  <div>
                    <h4 className="font-bold text-gray-900 mb-3">Benefits</h4>
                    <ul className="space-y-2">
                      {selectedTip.benefits.map((benefit, index) => (
                        <li key={index} className="flex gap-2 items-start">
                          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                          <span className="text-gray-700">{benefit}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {selectedTip.required_tools && selectedTip.required_tools.length > 0 && (
                  <div>
                    <h4 className="font-bold text-gray-900 mb-3">Required Tools</h4>
                    <ul className="space-y-2">
                      {selectedTip.required_tools.map((tool, index) => (
                        <li key={index} className="flex gap-2 items-center">
                          <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                          <span className="text-gray-700">{tool}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {showDeleteModal && selectedTip && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-bold text-gray-900">Delete Tip</h3>
              </div>
              <div className="p-6">
                <p className="text-gray-700">
                  Are you sure you want to delete this tip? This action cannot be undone.
                </p>
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <p className="font-medium text-gray-900">{selectedTip.title}</p>
                </div>
              </div>
              <div className="px-6 py-4 bg-gray-50 flex gap-3 justify-end">
                <button
                  onClick={() => {
                    setShowDeleteModal(false);
                    setSelectedTip(null);
                  }}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteTip}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default AdminTipsManagement;
