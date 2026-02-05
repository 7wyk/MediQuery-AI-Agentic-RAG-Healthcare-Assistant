import React, { useEffect, useState } from 'react';
import Navbar from '../components/layout/Navbar';
import { useAuth } from '../context/AuthContext';
import { FileText, MessageSquare, BarChart3, Upload } from 'lucide-react';
import { Link } from 'react-router-dom';
import documentsService from '../services/documents.service';
import analyticsService, { UsageOverview } from '../services/analytics.service';

const DashboardPage: React.FC = () => {
    const { user } = useAuth();
    const [stats, setStats] = useState<UsageOverview | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const data = await analyticsService.getOverview();
                setStats(data);
            } catch (error) {
                console.error('Failed to fetch stats:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    return (
        <div className="min-h-screen bg-gray-50">
            <Navbar />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Welcome Section */}
                <div className="mb-8">
                    <h1 className="text-3xl font-display font-bold text-gray-900 mb-2">
                        Welcome back, {user?.full_name}!
                    </h1>
                    <p className="text-gray-600">
                        {user?.role === 'doctor' ? 'Access your medical documents and research' : 'Continue your medical studies'}
                    </p>
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    {[
                        { icon: FileText, label: 'Documents', value: stats?.total_documents || 0, color: 'text-blue-600', bg: 'bg-blue-50' },
                        { icon: MessageSquare, label: 'Queries', value: stats?.total_queries || 0, color: 'text-purple-600', bg: 'bg-purple-50' },
                        { icon: BarChart3, label: 'Avg Response', value: `${stats?.avg_response_time.toFixed(2) || 0}s`, color: 'text-pink-600', bg: 'bg-pink-50' },
                        { icon: Upload, label: 'Tokens Used', value: stats?.total_tokens || 0, color: 'text-teal-600', bg: 'bg-teal-50' },
                    ].map((stat, i) => (
                        <div key={i} className="card">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-600 mb-1">{stat.label}</p>
                                    <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                                </div>
                                <div className={`w-12 h-12 ${stat.bg} rounded-lg flex items-center justify-center`}>
                                    <stat.icon className={`w-6 h-6 ${stat.color}`} />
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Quick Actions */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Link to="/documents" className="card card-hover group">
                        <FileText className="w-12 h-12 text-blue-600 mb-4" />
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">Manage Documents</h3>
                        <p className="text-gray-600">Upload, view, and organize your medical documents</p>
                    </Link>

                    <Link to="/chat" className="card card-hover group">
                        <MessageSquare className="w-12 h-12 text-purple-600 mb-4" />
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">Ask Questions</h3>
                        <p className="text-gray-600">Get instant answers from your documents using AI</p>
                    </Link>

                    <Link to="/analytics" className="card card-hover group">
                        <BarChart3 className="w-12 h-12 text-pink-600 mb-4" />
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">View Analytics</h3>
                        <p className="text-gray-600">Track your usage and query statistics</p>
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default DashboardPage;
