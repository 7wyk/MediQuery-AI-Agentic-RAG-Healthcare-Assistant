import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Shield, Zap, Globe, Users, FileText, MessageSquare, BarChart3 } from 'lucide-react';

const LandingPage: React.FC = () => {
    return (
        <div className="min-h-screen">
            {/* Hero Section */}
            <section className="relative bg-hero min-h-screen flex items-center justify-center overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-900/50 via-purple-900/50 to-pink-900/50"></div>

                <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                    <div className="animate-fade-in">
                        <h1 className="text-5xl md:text-7xl font-display font-bold text-white mb-6">
                            Medical Intelligence,
                            <br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-300 to-pink-300">
                                Powered by AI
                            </span>
                        </h1>

                        <p className="text-xl md:text-2xl text-gray-200 mb-8 max-w-3xl mx-auto">
                            Upload medical documents, ask questions, and get instant, accurate answers powered by advanced RAG technology and LLaMA3-70B.
                        </p>

                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            <Link
                                to="/register"
                                className="btn-primary inline-flex items-center justify-center gap-2 text-lg"
                            >
                                Get Started <ArrowRight className="w-5 h-5" />
                            </Link>
                            <Link
                                to="/login"
                                className="bg-white/10 backdrop-blur-md text-white border-2 border-white/30 font-semibold py-3 px-8 rounded-lg transition-all duration-300 hover:bg-white/20 inline-flex items-center justify-center"
                            >
                                Sign In
                            </Link>
                        </div>
                    </div>

                    {/* Floating Cards Preview */}
                    <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
                        {[
                            { icon: FileText, label: 'Upload Documents', color: 'from-blue-500 to-cyan-500' },
                            { icon: MessageSquare, label: 'Ask Questions', color: 'from-purple-500 to-pink-500' },
                            { icon: BarChart3, label: 'Track Analytics', color: 'from-pink-500 to-rose-500' },
                        ].map((item, i) => (
                            <div
                                key={i}
                                className="glass p-6 rounded-xl animate-slide-up"
                                style={{ animationDelay: `${i * 0.1}s` }}
                            >
                                <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${item.color} flex items-center justify-center mb-4 mx-auto`}>
                                    <item.icon className="w-6 h-6 text-white" />
                                </div>
                                <p className="text-white font-semibold">{item.label}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="py-20 bg-gray-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-display font-bold text-gray-900 mb-4">
                            Why Choose MediQuery AI?
                        </h2>
                        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                            Advanced features designed for medical professionals and students
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                        {[
                            {
                                icon: Shield,
                                title: 'Secure & Private',
                                description: 'Your medical documents are encrypted and isolated per user',
                                color: 'text-blue-600',
                            },
                            {
                                icon: Zap,
                                title: 'Lightning Fast',
                                description: 'Get answers in seconds with our optimized RAG pipeline',
                                color: 'text-purple-600',
                            },
                            {
                                icon: Globe,
                                title: 'Multi-Language',
                                description: 'Ask questions in any language, get accurate translations',
                                color: 'text-pink-600',
                            },
                            {
                                icon: Users,
                                title: 'Role-Based',
                                description: 'Tailored experience for doctors and medical students',
                                color: 'text-teal-600',
                            },
                        ].map((feature, i) => (
                            <div key={i} className="card card-hover text-center">
                                <feature.icon className={`w-12 h-12 ${feature.color} mx-auto mb-4`} />
                                <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
                                <p className="text-gray-600">{feature.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* How It Works */}
            <section className="py-20 bg-white">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-display font-bold text-gray-900 mb-4">
                            How It Works
                        </h2>
                        <p className="text-xl text-gray-600">Simple, fast, and intelligent</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
                        {[
                            { step: '1', title: 'Upload Documents', desc: 'Upload your medical PDFs, textbooks, or research papers' },
                            { step: '2', title: 'Ask Questions', desc: 'Type your medical questions in natural language' },
                            { step: '3', title: 'Get Answers', desc: 'Receive accurate, source-cited answers instantly' },
                        ].map((item, i) => (
                            <div key={i} className="text-center">
                                <div className="w-16 h-16 rounded-full bg-medical-gradient text-white text-2xl font-bold flex items-center justify-center mx-auto mb-4">
                                    {item.step}
                                </div>
                                <h3 className="text-2xl font-semibold text-gray-900 mb-2">{item.title}</h3>
                                <p className="text-gray-600">{item.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-20 bg-medical-gradient">
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                    <h2 className="text-4xl font-display font-bold text-white mb-6">
                        Ready to Transform Your Medical Research?
                    </h2>
                    <p className="text-xl text-gray-100 mb-8">
                        Join medical professionals and students using MediQuery AI
                    </p>
                    <Link
                        to="/register"
                        className="bg-white text-medical-blue font-semibold py-4 px-8 rounded-lg transition-all duration-300 hover:shadow-2xl hover:scale-105 inline-flex items-center gap-2"
                    >
                        Start Free Today <ArrowRight className="w-5 h-5" />
                    </Link>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-gray-900 text-gray-300 py-12">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
                        <div>
                            <h3 className="text-white font-semibold text-lg mb-4">MediQuery AI</h3>
                            <p className="text-sm">
                                Advanced medical document assistant powered by RAG and LLaMA3-70B
                            </p>
                        </div>
                        <div>
                            <h4 className="text-white font-semibold mb-4">Quick Links</h4>
                            <ul className="space-y-2 text-sm">
                                <li><Link to="/login" className="hover:text-white">Login</Link></li>
                                <li><Link to="/register" className="hover:text-white">Register</Link></li>
                            </ul>
                        </div>
                        <div>
                            <h4 className="text-white font-semibold mb-4">Legal</h4>
                            <p className="text-sm text-yellow-400">
                                ⚠️ Medical Disclaimer: This tool is for informational purposes only. Always consult qualified healthcare professionals for medical advice.
                            </p>
                        </div>
                    </div>
                    <div className="border-t border-gray-800 pt-8 text-center text-sm">
                        <p>&copy; 2026 MediQuery AI. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
