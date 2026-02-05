import React, { useState, useRef, useEffect } from 'react';
import Navbar from '../components/layout/Navbar';
import { Send, Loader, FileText, Trash2, Globe } from 'lucide-react';
import chatService, { ChatResponse } from '../services/chat.service';
import { useAuth } from '../context/AuthContext';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    sources?: any[];
    timestamp: Date;
}

const ChatPage: React.FC = () => {
    const { user } = useAuth();
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [showSources, setShowSources] = useState(false);
    const [currentSources, setCurrentSources] = useState<any[]>([]);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        const userMessage: Message = {
            role: 'user',
            content: input,
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response = await chatService.query({ question: input });

            const assistantMessage: Message = {
                role: 'assistant',
                content: response.answer,
                sources: response.sources,
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, assistantMessage]);
            setCurrentSources(response.sources);
        } catch (error: any) {
            const errorMessage: Message = {
                role: 'assistant',
                content: error.response?.data?.detail || 'Sorry, I encountered an error. Please try again.',
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const handleClearChat = () => {
        if (confirm('Clear all messages?')) {
            setMessages([]);
            setCurrentSources([]);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col">
            <Navbar />

            <div className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h1 className="text-3xl font-display font-bold text-gray-900 mb-2">
                            Medical Assistant Chat
                        </h1>
                        <p className="text-gray-600">
                            Ask questions about your uploaded documents
                        </p>
                    </div>

                    <div className="flex gap-2">
                        <button
                            onClick={() => setShowSources(!showSources)}
                            className="btn-ghost flex items-center gap-2"
                        >
                            <FileText className="w-4 h-4" />
                            Sources
                        </button>
                        <button
                            onClick={handleClearChat}
                            className="btn-ghost flex items-center gap-2 text-red-600 hover:bg-red-50"
                        >
                            <Trash2 className="w-4 h-4" />
                            Clear
                        </button>
                    </div>
                </div>

                {/* Chat Messages */}
                <div className="flex-1 card mb-6 flex flex-col overflow-hidden">
                    <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-4">
                        {messages.length === 0 ? (
                            <div className="text-center py-12">
                                <div className="w-16 h-16 bg-gradient-medical rounded-full flex items-center justify-center mx-auto mb-4">
                                    <FileText className="w-8 h-8 text-white" />
                                </div>
                                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                    Start a conversation
                                </h3>
                                <p className="text-gray-600">
                                    Ask me anything about your medical documents
                                </p>
                            </div>
                        ) : (
                            messages.map((message, i) => (
                                <div
                                    key={i}
                                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div
                                        className={`max-w-3xl rounded-lg p-4 ${message.role === 'user'
                                                ? 'bg-medical-gradient text-white'
                                                : 'bg-gray-100 text-gray-900'
                                            }`}
                                    >
                                        <p className="whitespace-pre-wrap">{message.content}</p>
                                        {message.sources && message.sources.length > 0 && (
                                            <button
                                                onClick={() => {
                                                    setCurrentSources(message.sources || []);
                                                    setShowSources(true);
                                                }}
                                                className="mt-2 text-sm underline opacity-75 hover:opacity-100"
                                            >
                                                View {message.sources.length} sources
                                            </button>
                                        )}
                                    </div>
                                </div>
                            ))
                        )}

                        {loading && (
                            <div className="flex justify-start">
                                <div className="bg-gray-100 rounded-lg p-4">
                                    <Loader className="w-5 h-5 text-medical-blue animate-spin" />
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Form */}
                    <form onSubmit={handleSubmit} className="border-t border-gray-200 p-4">
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Ask a medical question..."
                                className="flex-1 input"
                                disabled={loading}
                            />
                            <button
                                type="submit"
                                disabled={loading || !input.trim()}
                                className="btn-primary px-6"
                            >
                                <Send className="w-5 h-5" />
                            </button>
                        </div>
                    </form>
                </div>

                {/* Sources Panel */}
                {showSources && currentSources.length > 0 && (
                    <div className="card">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-gray-900">Source Documents</h3>
                            <button
                                onClick={() => setShowSources(false)}
                                className="text-gray-500 hover:text-gray-700"
                            >
                                Close
                            </button>
                        </div>
                        <div className="space-y-3">
                            {currentSources.map((source, i) => (
                                <div key={i} className="p-4 bg-gray-50 rounded-lg">
                                    <p className="text-sm text-gray-700 mb-2">{source.content}</p>
                                    <p className="text-xs text-gray-500">
                                        {source.metadata?.filename || 'Unknown source'} • Page {source.metadata?.page || 'N/A'}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ChatPage;
