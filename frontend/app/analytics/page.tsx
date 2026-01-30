'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { apiService, AnalyticsOverview, LanguageBreakdown, FeedbackStats, CacheStats, CostStats } from '@/services/api';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  Legend,
} from 'recharts';

// Color palettes
const LANGUAGE_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'];
const CACHE_COLORS = ['#10B981', '#EF4444'];

export default function AnalyticsPage() {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [languages, setLanguages] = useState<LanguageBreakdown[]>([]);
  const [feedbackStats, setFeedbackStats] = useState<FeedbackStats | null>(null);
  const [cacheStats, setCacheStats] = useState<CacheStats | null>(null);
  const [costStats, setCostStats] = useState<CostStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [overviewData, languageData, feedbackData, cacheData, costData] = await Promise.all([
          apiService.getAnalyticsOverview(),
          apiService.getLanguageBreakdown(),
          apiService.getFeedbackStats(),
          apiService.getCacheStats(),
          apiService.getCostStats(),
        ]);
        setOverview(overviewData);
        setLanguages(languageData);
        setFeedbackStats(feedbackData);
        setCacheStats(cacheData);
        setCostStats(costData);
      } catch (err) {
        setError('Failed to load analytics data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <main className="min-h-screen p-8 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-lg text-gray-600">Loading analytics...</div>
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen p-8 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="bg-red-100 text-red-700 p-4 rounded-lg">{error}</div>
        </div>
      </main>
    );
  }

  // Prepare chart data
  const dailyCostData = costStats?.daily?.map((day) => ({
    date: new Date(day.date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }),
    cost: day.cost,
  })) || [];

  const languageChartData = languages.map((lang) => ({
    name: lang.language.charAt(0).toUpperCase() + lang.language.slice(1),
    value: lang.total_errors,
    confidence: lang.avg_confidence,
  }));

  const feedbackChartData = feedbackStats?.solution_breakdown?.map((solution) => ({
    name: `Solution #${solution.solution_index + 1}`,
    successRate: Math.round(solution.success_rate * 100),
    successful: solution.successful,
    total: solution.total_feedback,
  })) || [];

  const cacheChartData = cacheStats?.enabled && !cacheStats?.error ? [
    { name: 'Hits', value: cacheStats.hits || 0 },
    { name: 'Misses', value: cacheStats.misses || 0 },
  ] : [];

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
            <p className="text-gray-600 mt-1">Monitor your DebugAI performance</p>
          </div>
          <Link
            href="/"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Back to Home
          </Link>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-sm font-medium text-gray-500 uppercase">Total Analyses</h3>
            <p className="text-3xl font-bold text-gray-900 mt-2">{overview?.total_analyses || 0}</p>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-sm font-medium text-gray-500 uppercase">Errors Parsed</h3>
            <p className="text-3xl font-bold text-gray-900 mt-2">{overview?.total_errors_parsed || 0}</p>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-sm font-medium text-gray-500 uppercase">Avg Analysis Time</h3>
            <p className="text-3xl font-bold text-gray-900 mt-2">{overview?.avg_analysis_time_ms || 0}ms</p>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-sm font-medium text-gray-500 uppercase">Success Rate</h3>
            <p className="text-3xl font-bold text-green-600 mt-2">
              {((overview?.feedback.success_rate || 0) * 100).toFixed(1)}%
            </p>
          </div>
        </div>

        {/* Cache Stats with Donut Chart */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Cache Performance</h2>
          {!cacheStats?.enabled ? (
            <p className="text-gray-500">{cacheStats?.message || 'Caching is disabled'}</p>
          ) : cacheStats?.error ? (
            <p className="text-red-500">Error: {cacheStats.error}</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-2xl font-bold text-gray-900">{cacheStats?.total_keys || 0}</p>
                  <p className="text-sm text-gray-500">Cached Keys</p>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">
                    {((cacheStats?.hit_rate || 0) * 100).toFixed(1)}%
                  </p>
                  <p className="text-sm text-gray-500">Hit Rate</p>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">{cacheStats?.hits || 0}</p>
                  <p className="text-sm text-gray-500">Cache Hits</p>
                </div>
                <div className="text-center p-4 bg-red-50 rounded-lg">
                  <p className="text-2xl font-bold text-red-600">{cacheStats?.misses || 0}</p>
                  <p className="text-sm text-gray-500">Cache Misses</p>
                </div>
              </div>
              {cacheChartData.length > 0 && (cacheChartData[0].value > 0 || cacheChartData[1].value > 0) && (
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={cacheChartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={70}
                        paddingAngle={5}
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
                      >
                        {cacheChartData.map((_, index) => (
                          <Cell key={`cell-${index}`} fill={CACHE_COLORS[index % CACHE_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Cost Tracking with Area Chart */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">API Cost Tracking (Last 30 Days)</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-2xl font-bold text-green-600">
                ${costStats?.total_cost?.toFixed(4) || '0.0000'}
              </p>
              <p className="text-sm text-gray-500">Total Cost</p>
            </div>
            {costStats?.breakdown?.map((item) => (
              <div key={item.operation} className="text-center p-4 bg-blue-50 rounded-lg">
                <p className="text-2xl font-bold text-blue-600">
                  ${item.total_cost.toFixed(4)}
                </p>
                <p className="text-sm text-gray-500 capitalize">{item.operation} ({item.count} calls)</p>
                <p className="text-xs text-gray-400">{item.total_tokens.toLocaleString()} tokens</p>
              </div>
            ))}
          </div>
          {dailyCostData.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-500 uppercase mb-3">Daily Costs (Last 7 Days)</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={dailyCostData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorCost" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                    <XAxis
                      dataKey="date"
                      tick={{ fontSize: 12, fill: '#6B7280' }}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fontSize: 12, fill: '#6B7280' }}
                      tickLine={false}
                      tickFormatter={(value) => `$${value.toFixed(4)}`}
                    />
                    <Tooltip
                      formatter={(value) => [`$${Number(value ?? 0).toFixed(4)}`, 'Cost']}
                      contentStyle={{
                        backgroundColor: '#fff',
                        border: '1px solid #E5E7EB',
                        borderRadius: '8px',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="cost"
                      stroke="#3B82F6"
                      fillOpacity={1}
                      fill="url(#colorCost)"
                      strokeWidth={2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Errors by Language - Pie Chart */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Errors by Language</h2>
            {languages.length === 0 ? (
              <p className="text-gray-500">No data yet</p>
            ) : (
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={languageChartData}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}`}
                    >
                      {languageChartData.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={LANGUAGE_COLORS[index % LANGUAGE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(value, _name, props) => [
                        `${value} errors (${props.payload.confidence}% avg confidence)`,
                        props.payload.confidence
                      ]}
                      contentStyle={{
                        backgroundColor: '#fff',
                        border: '1px solid #E5E7EB',
                        borderRadius: '8px'
                      }}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {/* Feedback Stats - Bar Chart */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Feedback Statistics</h2>
            <div className="space-y-4 mb-6">
              <div className="flex justify-between items-center pb-4 border-b">
                <span className="text-gray-600">Total Feedback</span>
                <span className="font-bold text-gray-900">{feedbackStats?.total_feedback || 0}</span>
              </div>
              <div className="flex justify-between items-center pb-4 border-b">
                <span className="text-gray-600">Successful Solutions</span>
                <span className="font-bold text-green-600">{feedbackStats?.total_successful || 0}</span>
              </div>
              <div className="flex justify-between items-center pb-4 border-b">
                <span className="text-gray-600">Overall Success Rate</span>
                <span className="font-bold text-blue-600">
                  {((feedbackStats?.overall_success_rate || 0) * 100).toFixed(1)}%
                </span>
              </div>
            </div>

            {/* Solution Success Rate Bar Chart */}
            {feedbackChartData.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-500 uppercase mb-3">Success Rate by Solution</h3>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={feedbackChartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                      <XAxis
                        dataKey="name"
                        tick={{ fontSize: 11, fill: '#6B7280' }}
                        tickLine={false}
                      />
                      <YAxis
                        tick={{ fontSize: 12, fill: '#6B7280' }}
                        tickLine={false}
                        domain={[0, 100]}
                        tickFormatter={(value) => `${value}%`}
                      />
                      <Tooltip
                        formatter={(value, _name, props) => [
                          `${value}% (${props.payload.successful}/${props.payload.total})`,
                          'Success Rate'
                        ]}
                        contentStyle={{
                          backgroundColor: '#fff',
                          border: '1px solid #E5E7EB',
                          borderRadius: '8px'
                        }}
                      />
                      <Bar
                        dataKey="successRate"
                        fill="#10B981"
                        radius={[4, 4, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
