'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { apiService, AnalyticsOverview, LanguageBreakdown, FeedbackStats, CacheStats, CostStats } from '@/services/api';

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

        {/* Cache Stats */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Cache Performance</h2>
          {!cacheStats?.enabled ? (
            <p className="text-gray-500">{cacheStats?.message || 'Caching is disabled'}</p>
          ) : cacheStats?.error ? (
            <p className="text-red-500">Error: {cacheStats.error}</p>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold text-gray-900">{cacheStats?.total_keys || 0}</p>
                <p className="text-sm text-gray-500">Cached Keys</p>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <p className="text-2xl font-bold text-green-600">{cacheStats?.hits || 0}</p>
                <p className="text-sm text-gray-500">Cache Hits</p>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <p className="text-2xl font-bold text-red-600">{cacheStats?.misses || 0}</p>
                <p className="text-sm text-gray-500">Cache Misses</p>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <p className="text-2xl font-bold text-blue-600">
                  {((cacheStats?.hit_rate || 0) * 100).toFixed(1)}%
                </p>
                <p className="text-sm text-gray-500">Hit Rate</p>
              </div>
            </div>
          )}
        </div>

        {/* Cost Tracking */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">API Cost Tracking (Last 30 Days)</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
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
          {costStats?.daily && costStats.daily.length > 0 && (
            <div className="mt-6">
              <h3 className="text-sm font-medium text-gray-500 uppercase mb-3">Daily Costs (Last 7 Days)</h3>
              <div className="flex items-end justify-between gap-2 h-32">
                {costStats.daily.map((day) => (
                  <div key={day.date} className="flex-1 flex flex-col items-center">
                    <div
                      className="w-full bg-blue-500 rounded-t"
                      style={{
                        height: `${Math.max((day.cost / Math.max(...costStats.daily.map(d => d.cost))) * 100, 5)}%`,
                        minHeight: '4px'
                      }}
                    />
                    <p className="text-xs text-gray-500 mt-1">{new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })}</p>
                    <p className="text-xs text-gray-400">${day.cost.toFixed(4)}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Errors by Language */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Errors by Language</h2>
            {languages.length === 0 ? (
              <p className="text-gray-500">No data yet</p>
            ) : (
              <div className="space-y-3">
                {languages.map((lang) => (
                  <div key={lang.language} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="font-medium text-gray-900 capitalize">{lang.language}</span>
                      <span className="text-sm text-gray-500">
                        ({lang.avg_confidence}% avg confidence)
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-32 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{
                            width: `${Math.min((lang.total_errors / (overview?.total_errors_parsed || 1)) * 100, 100)}%`,
                          }}
                        />
                      </div>
                      <span className="text-sm font-medium text-gray-700 w-8">{lang.total_errors}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Feedback Stats */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Feedback Statistics</h2>
            <div className="space-y-4">
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

              {/* Solution Breakdown */}
              {feedbackStats?.solution_breakdown && feedbackStats.solution_breakdown.length > 0 && (
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-500 uppercase mb-3">By Solution Position</h3>
                  <div className="space-y-2">
                    {feedbackStats.solution_breakdown.map((solution) => (
                      <div key={solution.solution_index} className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Solution #{solution.solution_index + 1}</span>
                        <div className="flex items-center gap-4">
                          <span className="text-gray-500">
                            {solution.successful}/{solution.total_feedback} worked
                          </span>
                          <span className={`font-medium ${solution.success_rate >= 0.7 ? 'text-green-600' : solution.success_rate >= 0.4 ? 'text-yellow-600' : 'text-red-600'}`}>
                            {(solution.success_rate * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
