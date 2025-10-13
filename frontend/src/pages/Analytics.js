import React, { useState, useEffect } from 'react';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';
import toast from 'react-hot-toast';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Droplets,
  DollarSign,
  Calendar,
  Download,
  Activity,
  Minus
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

export const Analytics = () => {
  const { user } = useAuth();
  const [period, setPeriod] = useState('month');
  const [usageData, setUsageData] = useState(null);
  const [trendsData, setTrendsData] = useState(null);
  const [predictionsData, setPredictionsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('usage');

  useEffect(() => {
    fetchAnalytics();
  }, [period]);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch usage data
      const usageResponse = await axios.get(
        `${BACKEND_URL}/api/analytics/usage?period=${period}`,
        { headers }
      );
      setUsageData(usageResponse.data);

      // Fetch trends
      const trendsResponse = await axios.get(
        `${BACKEND_URL}/api/analytics/trends?period=${period}`,
        { headers }
      );
      setTrendsData(trendsResponse.data);

      // Fetch predictions
      if (user.role === 'customer' || user.id) {
        try {
          const predictionsResponse = await axios.get(
            `${BACKEND_URL}/api/analytics/predictions?days_ahead=7`,
            { headers }
          );
          setPredictionsData(predictionsResponse.data);
        } catch (error) {
          // Predictions might not be available for all users
          console.log('Predictions not available');
        }
      }

    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      toast.error('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format) => {
    try {
      const token = localStorage.getItem('token');
      
      const requestData = {
        start_date: usageData.start_date.split('T')[0],
        end_date: usageData.end_date.split('T')[0],
        include_charts: true
      };

      const endpoint = format === 'pdf' ? 'export-pdf' : 'export-excel';
      
      const response = await axios.post(
        `${BACKEND_URL}/api/reports/${endpoint}`,
        requestData,
        {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob'
        }
      );

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `water_usage_report.${format === 'pdf' ? 'pdf' : 'xlsx'}`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success(`${format.toUpperCase()} report downloaded`);
    } catch (error) {
      console.error('Export failed:', error);
      toast.error(`Failed to export ${format.toUpperCase()}`);
    }
  };

  const getTrendIcon = (trend) => {
    if (trend === 'increasing') return <TrendingUp className="h-5 w-5 text-red-500" />;
    if (trend === 'decreasing') return <TrendingDown className="h-5 w-5 text-green-500" />;
    return <Minus className="h-5 w-5 text-gray-500" />;
  };

  const formatChartData = (dataPoints) => {
    return dataPoints.map(point => ({
      date: point.date.split('T')[0],
      consumption: parseFloat(point.consumption.toFixed(3)),
      cost: parseFloat(point.cost.toFixed(2))
    }));
  };

  if (loading && !usageData) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <Activity className="h-12 w-12 text-blue-600 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">Loading analytics...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Water Usage Analytics</h1>
          <p className="text-gray-600">Track and analyze your water consumption patterns</p>
        </div>

        {/* Period Selector */}
        <div className="flex justify-between items-center mb-6">
          <div className="flex gap-2">
            {['day', 'week', 'month', 'year'].map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  period === p
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {p.charAt(0).toUpperCase() + p.slice(1)}
              </button>
            ))}
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => handleExport('pdf')}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
            >
              <Download className="h-4 w-4" />
              PDF
            </button>
            <button
              onClick={() => handleExport('excel')}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
            >
              <Download className="h-4 w-4" />
              Excel
            </button>
          </div>
        </div>

        {usageData && (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-xl shadow-md p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-600 text-sm">Total Consumption</span>
                  <Droplets className="h-5 w-5 text-blue-600" />
                </div>
                <p className="text-2xl font-bold text-gray-900">
                  {usageData.total_consumption.toFixed(2)} m³
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  Avg: {usageData.average_daily.toFixed(3)} m³/day
                </p>
              </div>

              <div className="bg-white rounded-xl shadow-md p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-600 text-sm">Total Cost</span>
                  <DollarSign className="h-5 w-5 text-green-600" />
                </div>
                <p className="text-2xl font-bold text-gray-900">
                  Rp {usageData.total_cost.toLocaleString('id-ID')}
                </p>
              </div>

              <div className="bg-white rounded-xl shadow-md p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-600 text-sm">Active Devices</span>
                  <Activity className="h-5 w-5 text-purple-600" />
                </div>
                <p className="text-2xl font-bold text-gray-900">{usageData.device_count}</p>
              </div>

              <div className="bg-white rounded-xl shadow-md p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-600 text-sm">Trend</span>
                  <Calendar className="h-5 w-5 text-orange-600" />
                </div>
                <div className="flex items-center gap-2">
                  {trendsData && getTrendIcon(trendsData.overall_trend)}
                  <span className="text-2xl font-bold text-gray-900 capitalize">
                    {trendsData?.overall_trend || 'Stable'}
                  </span>
                </div>
                {trendsData && (
                  <p className="text-sm text-gray-500 mt-1">
                    {trendsData.growth_rate > 0 ? '+' : ''}
                    {trendsData.growth_rate.toFixed(1)}% change
                  </p>
                )}
              </div>
            </div>

            {/* Tabs */}
            <div className="mb-6">
              <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8">
                  {['usage', 'trends', 'predictions'].map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`py-2 px-1 border-b-2 font-medium text-sm transition ${
                        activeTab === tab
                          ? 'border-blue-600 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                    >
                      {tab.charAt(0).toUpperCase() + tab.slice(1)}
                    </button>
                  ))}
                </nav>
              </div>
            </div>

            {/* Charts */}
            {activeTab === 'usage' && (
              <div className="bg-white rounded-xl shadow-md p-6 mb-8">
                <h2 className="text-xl font-bold text-gray-900 mb-6">Daily Consumption</h2>
                <ResponsiveContainer width="100%" height={400}>
                  <AreaChart data={formatChartData(usageData.data_points)}>
                    <defs>
                      <linearGradient id="colorConsumption" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="date"
                      tick={{ fontSize: 12 }}
                      tickFormatter={(value) => value.split('-').slice(1).join('/')}
                    />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip
                      formatter={(value, name) => {
                        if (name === 'consumption') return [value + ' m³', 'Consumption'];
                        if (name === 'cost') return ['Rp ' + value.toLocaleString('id-ID'), 'Cost'];
                        return [value, name];
                      }}
                    />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="consumption"
                      stroke="#3B82F6"
                      fillOpacity={1}
                      fill="url(#colorConsumption)"
                      name="Consumption (m³)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}

            {activeTab === 'trends' && trendsData && (
              <div className="bg-white rounded-xl shadow-md p-6 mb-8">
                <h2 className="text-xl font-bold text-gray-900 mb-6">Consumption Trends</h2>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={trendsData.trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip
                      formatter={(value) => [value + ' m³', 'Consumption']}
                    />
                    <Legend />
                    <Bar dataKey="consumption" fill="#3B82F6" name="Consumption (m³)" />
                  </BarChart>
                </ResponsiveContainer>

                {/* Trend Details */}
                <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                  {trendsData.trends.slice(-3).map((trend, idx) => (
                    <div key={idx} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-600">{trend.period}</span>
                        {getTrendIcon(trend.trend)}
                      </div>
                      <p className="text-lg font-bold text-gray-900">
                        {trend.consumption.toFixed(2)} m³
                      </p>
                      {trend.percentage_change !== null && (
                        <p className={`text-sm mt-1 ${
                          trend.percentage_change > 0 ? 'text-red-600' : 'text-green-600'
                        }`}>
                          {trend.percentage_change > 0 ? '+' : ''}
                          {trend.percentage_change.toFixed(1)}% from previous
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'predictions' && predictionsData && (
              <div className="bg-white rounded-xl shadow-md p-6 mb-8">
                <h2 className="text-xl font-bold text-gray-900 mb-2">Usage Predictions</h2>
                <p className="text-sm text-gray-600 mb-6">{predictionsData.notes}</p>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={predictionsData.predictions}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip
                      formatter={(value) => [value + ' m³', 'Predicted Consumption']}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="predicted_consumption"
                      stroke="#8B5CF6"
                      strokeWidth={2}
                      dot={{ r: 4 }}
                      name="Predicted (m³)"
                    />
                    <Line
                      type="monotone"
                      dataKey="confidence_upper"
                      stroke="#D1D5DB"
                      strokeDasharray="5 5"
                      dot={false}
                      name="Upper Bound"
                    />
                    <Line
                      type="monotone"
                      dataKey="confidence_lower"
                      stroke="#D1D5DB"
                      strokeDasharray="5 5"
                      dot={false}
                      name="Lower Bound"
                    />
                  </LineChart>
                </ResponsiveContainer>

                <div className="mt-6 bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <h3 className="font-semibold text-purple-900 mb-2">Next 7 Days Forecast</h3>
                  <p className="text-purple-800">
                    Average predicted consumption: <span className="font-bold">
                      {predictionsData.average_predicted.toFixed(3)} m³/day
                    </span>
                  </p>
                  <p className="text-sm text-purple-700 mt-1">
                    Based on {predictionsData.based_on_days} days of historical data
                  </p>
                </div>
              </div>
            )}

            {activeTab === 'predictions' && !predictionsData && (
              <div className="bg-white rounded-xl shadow-md p-6 mb-8 text-center">
                <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">
                  Predictions require at least 7 days of historical data
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </Layout>
  );
};
