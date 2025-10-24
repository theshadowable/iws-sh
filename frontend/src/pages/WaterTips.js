import React, { useState, useEffect } from 'react';
import { Search, Filter, Lightbulb, Heart, Bookmark, CheckCircle, TrendingDown, Clock, BookOpen } from 'lucide-react';
import Layout from '../components/Layout';

const WaterTips = () => {
  const [tips, setTips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [difficultyFilter, setDifficultyFilter] = useState('all');
  const [selectedTip, setSelectedTip] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [engagements, setEngagements] = useState({});

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    fetchTips();
  }, [categoryFilter, difficultyFilter]);

  const fetchTips = async () => {
    try {
      const token = localStorage.getItem('token');
      let url = `${BACKEND_URL}/api/tips?limit=100`;
      
      if (categoryFilter !== 'all') {
        url += `&category=${categoryFilter}`;
      }
      if (difficultyFilter !== 'all') {
        url += `&difficulty=${difficultyFilter}`;
      }

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setTips(data.tips);
      }
    } catch (error) {
      console.error('Error fetching tips:', error);
    } finally {
      setLoading(false);
    }
  };

  const viewTipDetail = async (tipId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/tips/${tipId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSelectedTip(data);
        setEngagements({
          liked: data.is_liked,
          bookmarked: data.is_bookmarked,
          implemented: data.is_implemented
        });
        setShowModal(true);
      }
    } catch (error) {
      console.error('Error fetching tip detail:', error);
    }
  };

  const handleEngage = async (action) => {
    if (!selectedTip) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/tips/${selectedTip.tip.id}/engage`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action })
      });

      if (response.ok) {
        // Update local engagement state
        if (action === 'like') {
          setEngagements({ ...engagements, liked: true });
          setSelectedTip({
            ...selectedTip,
            tip: { ...selectedTip.tip, like_count: selectedTip.tip.like_count + 1 }
          });
        } else if (action === 'unlike') {
          setEngagements({ ...engagements, liked: false });
          setSelectedTip({
            ...selectedTip,
            tip: { ...selectedTip.tip, like_count: Math.max(0, selectedTip.tip.like_count - 1) }
          });
        } else if (action === 'bookmark') {
          setEngagements({ ...engagements, bookmarked: true });
        } else if (action === 'unbookmark') {
          setEngagements({ ...engagements, bookmarked: false });
        } else if (action === 'implement') {
          setEngagements({ ...engagements, implemented: true });
          setSelectedTip({
            ...selectedTip,
            tip: { ...selectedTip.tip, implementation_count: selectedTip.tip.implementation_count + 1 }
          });
        }
        
        // Refresh tips list
        fetchTips();
      }
    } catch (error) {
      console.error('Error engaging with tip:', error);
    }
  };

  const getCategoryLabel = (category) => {
    const labels = {
      'general_savings': 'Penghematan Umum',
      'leak_prevention': 'Pencegahan Kebocoran',
      'best_practices': 'Praktik Terbaik',
      'saran_penghematan_prabayar': 'Tips Prabayar'
    };
    return labels[category] || category;
  };

  const getCategoryColor = (category) => {
    const colors = {
      'general_savings': 'bg-blue-100 text-blue-800',
      'leak_prevention': 'bg-red-100 text-red-800',
      'best_practices': 'bg-green-100 text-green-800',
      'saran_penghematan_prabayar': 'bg-purple-100 text-purple-800'
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  const getDifficultyColor = (level) => {
    const colors = {
      'easy': 'bg-green-100 text-green-700',
      'medium': 'bg-yellow-100 text-yellow-700',
      'hard': 'bg-red-100 text-red-700'
    };
    return colors[level] || 'bg-gray-100 text-gray-700';
  };

  const filteredTips = tips.filter(tip =>
    tip.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    tip.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (tip.tags && tip.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase())))
  );

  return (
    <Layout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Lightbulb className="w-8 h-8 text-yellow-500" />
            Water Conservation Tips
          </h1>
          <p className="text-gray-600 mt-1">Learn how to save water and reduce your costs</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg shadow p-4 border border-blue-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-600 rounded-lg">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-sm text-blue-700">Total Tips</p>
                <p className="text-2xl font-bold text-blue-900">{tips.length}</p>
              </div>
            </div>
          </div>
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg shadow p-4 border border-green-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-green-600 rounded-lg">
                <TrendingDown className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-sm text-green-700">Avg. Savings</p>
                <p className="text-2xl font-bold text-green-900">
                  {tips.length > 0 ? Math.round(tips.reduce((sum, t) => sum + (t.potential_savings_percentage || 0), 0) / tips.length) : 0}%
                </p>
              </div>
            </div>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg shadow p-4 border border-purple-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-purple-600 rounded-lg">
                <Clock className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-sm text-purple-700">Easy Tips</p>
                <p className="text-2xl font-bold text-purple-900">
                  {tips.filter(t => t.difficulty_level === 'easy').length}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg shadow p-4 border border-yellow-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-yellow-600 rounded-lg">
                <Lightbulb className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-sm text-yellow-700">Categories</p>
                <p className="text-2xl font-bold text-yellow-900">4</p>
              </div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
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
            </div>

            {/* Category Filter */}
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Categories</option>
              <option value="general_savings">Penghematan Umum</option>
              <option value="leak_prevention">Pencegahan Kebocoran</option>
              <option value="best_practices">Praktik Terbaik</option>
              <option value="saran_penghematan_prabayar">Tips Prabayar</option>
            </select>

            {/* Difficulty Filter */}
            <select
              value={difficultyFilter}
              onChange={(e) => setDifficultyFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Difficulty</option>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
        </div>

        {/* Tips Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading tips...</p>
          </div>
        ) : filteredTips.length === 0 ? (
          <div className="text-center py-12">
            <Lightbulb className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No tips found matching your criteria</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTips.map((tip) => (
              <div
                key={tip.id}
                onClick={() => viewTipDetail(tip.id)}
                className="bg-white rounded-lg shadow hover:shadow-xl transition-shadow cursor-pointer border border-gray-200"
              >
                <div className="p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(tip.category)} mb-2`}>
                        {getCategoryLabel(tip.category)}
                      </span>
                      <h3 className="text-lg font-bold text-gray-900 leading-tight">
                        {tip.title}
                      </h3>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(tip.difficulty_level)}`}>
                      {tip.difficulty_level}
                    </span>
                  </div>

                  {/* Description */}
                  <p className="text-gray-600 text-sm line-clamp-3 mb-4">
                    {tip.description}
                  </p>

                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-2 mb-4">
                    {tip.potential_savings_percentage && (
                      <div className="bg-green-50 rounded p-2 text-center">
                        <TrendingDown className="w-4 h-4 text-green-600 mx-auto mb-1" />
                        <p className="text-xs text-gray-600">Hemat</p>
                        <p className="text-sm font-bold text-green-600">{tip.potential_savings_percentage}%</p>
                      </div>
                    )}
                    {tip.implementation_time && (
                      <div className="bg-blue-50 rounded p-2 text-center">
                        <Clock className="w-4 h-4 text-blue-600 mx-auto mb-1" />
                        <p className="text-xs text-gray-600">Waktu</p>
                        <p className="text-xs font-bold text-blue-600">{tip.implementation_time}</p>
                      </div>
                    )}
                  </div>

                  {/* Engagement */}
                  <div className="flex items-center justify-between text-xs text-gray-500 border-t pt-3">
                    <span className="flex items-center gap-1">
                      <Heart className="w-4 h-4" />
                      {tip.like_count}
                    </span>
                    <span className="flex items-center gap-1">
                      <CheckCircle className="w-4 h-4" />
                      {tip.implementation_count}
                    </span>
                    <span>{tip.view_count} views</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Tip Detail Modal */}
        {showModal && selectedTip && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setShowModal(false)}>
            <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
              <div className="p-6">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${getCategoryColor(selectedTip.tip.category)} mb-2`}>
                      {getCategoryLabel(selectedTip.tip.category)}
                    </span>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">{selectedTip.tip.title}</h2>
                  </div>
                  <button
                    onClick={() => setShowModal(false)}
                    className="text-gray-400 hover:text-gray-600 text-2xl"
                  >
                    ×
                  </button>
                </div>

                {/* Description */}
                <p className="text-gray-700 leading-relaxed mb-6">{selectedTip.tip.description}</p>

                {/* Stats Grid */}
                <div className="grid grid-cols-3 gap-3 mb-6">
                  {selectedTip.tip.potential_savings_percentage && (
                    <div className="bg-green-50 rounded-lg p-4 text-center">
                      <TrendingDown className="w-6 h-6 text-green-600 mx-auto mb-2" />
                      <p className="text-xs text-gray-600">Hemat</p>
                      <p className="text-xl font-bold text-green-600">{selectedTip.tip.potential_savings_percentage}%</p>
                    </div>
                  )}
                  {selectedTip.tip.implementation_time && (
                    <div className="bg-blue-50 rounded-lg p-4 text-center">
                      <Clock className="w-6 h-6 text-blue-600 mx-auto mb-2" />
                      <p className="text-xs text-gray-600">Waktu</p>
                      <p className="text-sm font-bold text-blue-600">{selectedTip.tip.implementation_time}</p>
                    </div>
                  )}
                  {selectedTip.tip.potential_savings_amount && (
                    <div className="bg-purple-50 rounded-lg p-4 text-center">
                      <p className="text-xs text-gray-600 mb-1">Hemat/Bulan</p>
                      <p className="text-sm font-bold text-purple-600">
                        Rp {selectedTip.tip.potential_savings_amount.toLocaleString()}
                      </p>
                    </div>
                  )}
                </div>

                {/* Difficulty */}
                <div className="mb-6">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColor(selectedTip.tip.difficulty_level)}`}>
                    Difficulty: {selectedTip.tip.difficulty_level}
                  </span>
                </div>

                {/* Tags */}
                {selectedTip.tip.tags && selectedTip.tip.tags.length > 0 && (
                  <div className="mb-6">
                    <p className="text-sm font-medium text-gray-700 mb-2">Tags:</p>
                    <div className="flex flex-wrap gap-2">
                      {selectedTip.tip.tags.map((tag, index) => (
                        <span key={index} className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-xs">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Engagement Stats */}
                <div className="flex items-center gap-6 mb-6 text-sm text-gray-600 border-t pt-4">
                  <span>{selectedTip.tip.view_count} views</span>
                  <span>{selectedTip.tip.like_count} likes</span>
                  <span>{selectedTip.tip.implementation_count} implemented</span>
                </div>

                {/* Actions */}
                <div className="flex gap-3">
                  <button
                    onClick={() => handleEngage(engagements.liked ? 'unlike' : 'like')}
                    className={`flex-1 px-4 py-2 rounded-lg transition-colors flex items-center justify-center gap-2 ${
                      engagements.liked
                        ? 'bg-red-600 text-white hover:bg-red-700'
                        : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <Heart className={`w-5 h-5 ${engagements.liked ? 'fill-current' : ''}`} />
                    {engagements.liked ? 'Liked' : 'Like'}
                  </button>
                  <button
                    onClick={() => handleEngage(engagements.bookmarked ? 'unbookmark' : 'bookmark')}
                    className={`flex-1 px-4 py-2 rounded-lg transition-colors flex items-center justify-center gap-2 ${
                      engagements.bookmarked
                        ? 'bg-yellow-600 text-white hover:bg-yellow-700'
                        : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <Bookmark className={`w-5 h-5 ${engagements.bookmarked ? 'fill-current' : ''}`} />
                    {engagements.bookmarked ? 'Saved' : 'Save'}
                  </button>
                  <button
                    onClick={() => handleEngage(engagements.implemented ? 'unimplement' : 'implement')}
                    className={`flex-1 px-4 py-2 rounded-lg transition-colors flex items-center justify-center gap-2 ${
                      engagements.implemented
                        ? 'bg-green-600 text-white hover:bg-green-700'
                        : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <CheckCircle className={`w-5 h-5 ${engagements.implemented ? 'fill-current' : ''}`} />
                    {engagements.implemented ? 'Implemented' : 'Implement'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default WaterTips;
