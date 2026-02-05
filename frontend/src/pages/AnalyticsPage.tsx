import React, { useEffect, useState } from 'react';
import Navbar from '../components/layout/Navbar';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import analyticsService, { UsageOverview, UsageGraphData, TopTopics } from '../services/analytics.service';
import LoadingSpinner from '../components/common/LoadingSpinner';

const AnalyticsPage: React.FC = () => {
    const [overview, setOverview] = useState<UsageOverview | null>(null);
    const [graphData, setGraphData] = useState<UsageGraphData | null>(null);
    const [topics, setTopics] = useState<TopTopics | null>(null);
    const [loading, setLoading] = useState(true);
    const [period, setPeriod] = useState<'daily' | 'weekly'>('daily');

    useEffect(() => {
        const fetchAnalytics = async () => {
            try {
                const [overviewData, graphDataRes, topicsData] = await Promise.all([
                    analyticsService.getOverview(),
                    analyticsService.getUsageGraph(period),
                    analyticsService.getTopTopics(5),
                ]);

                setOverview(overviewData);
                setGraphData(graphDataRes);
                setTopics(topicsData);
            } catch (error) {
                console.error('Failed to fetch analytics:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchAnalytics();
    }, [period]);

    const COLORS = ['#4F46E5', '#7C3AED', '#EC4899', '#14B8A6', '#F59E0B'];

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50">
                <Navbar />
                <LoadingSpinner className="mt-20" size="lg" />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <Navbar />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-display font-bold text-gray-900 mb-2">
                        Usage Analytics
                    </h1>
                    <p className="text-gray-600">Track your activity and usage patterns</p>
                </div>

                {/* Overview Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <div className="card">
                        <p className="text-sm text-gray-600 mb-1">Total Documents</p>
                        <p className="text-3xl font-bold text-gray-900">{overview?.total_documents || 0}</p>
                    </div>
                    <div className="card">
                        <p className="text-sm text-gray-600 mb-1">Total Queries</p>
                        <p className="text-3xl font-bold text-gray-900">{overview?.total_queries || 0}</p>
                    </div>
                    <div className="card">
                        <p className="text-sm text-gray-600 mb-1">Avg Response Time</p>
                        <p className="text-3xl font-bold text-gray-900">{overview?.avg_response_time.toFixed(2) || 0}s</p>
                    </div>
                    <div className="card">
                        <p className="text-sm text-gray-600 mb-1">Total Tokens</p>
                        <p className="text-3xl font-bold text-gray-900">{overview?.total_tokens.toLocaleString() || 0}</p>
                    </div>
                </div>

                {/* Usage Graph */}
                <div className="card mb-8">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-xl font-semibold text-gray-900">Query Activity</h2>
                        <div className="flex gap-2">
                            <button
                                onClick={() => setPeriod('daily')}
                                className={`px-4 py-2 rounded-lg transition-colors ${period === 'daily'
                                        ? 'bg-medical-blue text-white'
                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                    }`}
                            >
                                Daily
                            </button>
                            <button
                                onClick={() => setPeriod('weekly')}
                                className={`px-4 py-2 rounded-lg transition-colors ${period === 'weekly'
                                        ? 'bg-medical-blue text-white'
                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                    }`}
                            >
                                Weekly
                            </button>
                        </div>
                    </div>

                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={graphData?.data_points || []}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="queries" stroke="#4F46E5" strokeWidth={2} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>

                {/* Top Topics */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div className="card">
                        <h2 className="text-xl font-semibold text-gray-900 mb-6">Top Topics</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={topics?.topics || []}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="topic" />
                                <YAxis />
                                <Tooltip />
                                <Bar dataKey="count" fill="#7C3AED" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    <div className="card">
                        <h2 className="text-xl font-semibold text-gray-900 mb-6">Topic Distribution</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={topics?.topics || []}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={(entry) => entry.topic}
                                    outerRadius={100}
                                    fill="#8884d8"
                                    dataKey="count"
                                >
                                    {(topics?.topics || []).map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AnalyticsPage;
