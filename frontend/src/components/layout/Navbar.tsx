import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { LogOut, User, Menu, X } from 'lucide-react';

const Navbar: React.FC = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    <div className="flex items-center">
                        <Link to="/dashboard" className="text-2xl font-display font-bold text-gradient">
                            MediQuery AI
                        </Link>
                    </div>

                    {/* Desktop Menu */}
                    <div className="hidden md:flex items-center gap-6">
                        <Link to="/dashboard" className="btn-ghost">Dashboard</Link>
                        <Link to="/documents" className="btn-ghost">Documents</Link>
                        <Link to="/chat" className="btn-ghost">Chat</Link>
                        <Link to="/analytics" className="btn-ghost">Analytics</Link>

                        <div className="flex items-center gap-3 ml-4 pl-4 border-l border-gray-200">
                            <div className="text-right">
                                <div className="text-sm font-semibold text-gray-900">{user?.full_name}</div>
                                <div className="text-xs text-gray-500 capitalize">{user?.role}</div>
                            </div>
                            <button
                                onClick={handleLogout}
                                className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                title="Logout"
                            >
                                <LogOut className="w-5 h-5" />
                            </button>
                        </div>
                    </div>

                    {/* Mobile Menu Button */}
                    <div className="md:hidden flex items-center">
                        <button
                            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                            className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                        >
                            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            {mobileMenuOpen && (
                <div className="md:hidden border-t border-gray-200 bg-white">
                    <div className="px-4 py-4 space-y-2">
                        <Link to="/dashboard" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Dashboard</Link>
                        <Link to="/documents" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Documents</Link>
                        <Link to="/chat" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Chat</Link>
                        <Link to="/analytics" className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">Analytics</Link>
                        <button
                            onClick={handleLogout}
                            className="w-full text-left px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg"
                        >
                            Logout
                        </button>
                    </div>
                </div>
            )}
        </nav>
    );
};

export default Navbar;
