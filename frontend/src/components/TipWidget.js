import React, { useState, useEffect } from 'react';
import { Lightbulb, TrendingDown, Clock, Heart, Bookmark, CheckCircle, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const TipWidget = ({ compact = false }) => {
  const [tip, setTip] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    fetchRandomTip();
  }, []);

  const fetchRandomTip = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/tips/random`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setTip(data);
      }
    } catch (error) {
      console.error('Error fetching tip:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (level) => {
    switch (level) {
      case 'easy': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'hard': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
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

  if (loading) {
    return (
      <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-6 border border-blue-200 animate-pulse">
        <div className="h-6 bg-blue-200 rounded w-3/4 mb-3"></div>
        <div className="h-4 bg-blue-200 rounded w-full mb-2"></div>
        <div className="h-4 bg-blue-200 rounded w-5/6"></div>
      </div>
    );
  }

  if (!tip) {
    return (
      <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-6 border border-blue-200">
        <p className="text-gray-600">No tips available</p>
      </div>
    );
  }

  if (compact) {
    return (
      <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-4 border border-blue-200 cursor-pointer hover:shadow-md transition-shadow" onClick={() => navigate('/tips')}>
        <div className="flex items-start gap-3">
          <div className="p-2 bg-blue-600 rounded-lg">
            <Lightbulb className="w-5 h-5 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-blue-900 truncate">{tip.title}</p>
            <p className="text-xs text-blue-700 mt-1 line-clamp-2">{tip.description}</p>
            <button className="text-xs text-blue-600 font-medium mt-2 flex items-center gap-1 hover:text-blue-800">
              Lihat Semua Tips <ChevronRight className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50 rounded-xl p-6 border border-blue-200 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-blue-600 rounded-lg">
            <Lightbulb className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-blue-900">💡 Water Saving Tip</h3>
            <p className="text-xs text-blue-600">{getCategoryLabel(tip.category)}</p>
          </div>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getDifficultyColor(tip.difficulty_level)}`}>
          {tip.difficulty_level}
        </span>
      </div>

      {/* Content */}
      <div className="mb-4">
        <h4 className="text-xl font-bold text-gray-900 mb-2">{tip.title}</h4>
        <p className="text-gray-700 leading-relaxed">{tip.description}</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        {tip.potential_savings_percentage && (
          <div className="bg-white rounded-lg p-3 text-center">
            <TrendingDown className="w-5 h-5 text-green-600 mx-auto mb-1" />
            <p className="text-xs text-gray-600">Hemat</p>
            <p className="text-lg font-bold text-green-600">{tip.potential_savings_percentage}%</p>
          </div>
        )}
        {tip.implementation_time && (
          <div className="bg-white rounded-lg p-3 text-center">
            <Clock className="w-5 h-5 text-blue-600 mx-auto mb-1" />
            <p className="text-xs text-gray-600">Waktu</p>
            <p className="text-sm font-bold text-blue-600">{tip.implementation_time}</p>
          </div>
        )}
        {tip.potential_savings_amount && (
          <div className="bg-white rounded-lg p-3 text-center">
            <p className="text-xs text-gray-600">Hemat/Bulan</p>
            <p className="text-sm font-bold text-green-600">Rp {tip.potential_savings_amount.toLocaleString()}</p>
          </div>
        )}
      </div>

      {/* Engagement Stats */}
      <div className="flex items-center gap-4 text-xs text-gray-600 mb-4">
        <span className="flex items-center gap-1">
          <Heart className="w-4 h-4" />
          {tip.like_count}
        </span>
        <span className="flex items-center gap-1">
          <CheckCircle className="w-4 h-4" />
          {tip.implementation_count} implemented
        </span>
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <button
          onClick={() => navigate('/tips')}
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          Lihat Semua Tips
        </button>
        <button
          onClick={fetchRandomTip}
          className="px-4 py-2 bg-white border border-blue-300 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors font-medium"
        >
          Tip Lain
        </button>
      </div>
    </div>
  );
};

export default TipWidget;