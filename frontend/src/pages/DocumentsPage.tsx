import React, { useEffect, useState, useCallback } from 'react';
import Navbar from '../components/layout/Navbar';
import { Upload, FileText, Trash2, RefreshCw, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import documentsService, { Document } from '../services/documents.service';
import { formatFileSize, formatDate } from '../lib/utils';

const DocumentsPage: React.FC = () => {
    const [documents, setDocuments] = useState<Document[]>([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);

    const fetchDocuments = useCallback(async () => {
        try {
            const data = await documentsService.list();
            setDocuments(data.documents);
        } catch (error) {
            console.error('Failed to fetch documents:', error);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchDocuments();
    }, [fetchDocuments]);

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (!files || files.length === 0) return;

        setUploading(true);
        setUploadProgress(0);

        try {
            await documentsService.upload(files, (progress) => {
                setUploadProgress(progress);
            });
            await fetchDocuments();
        } catch (error: any) {
            alert(error.response?.data?.detail || 'Upload failed');
        } finally {
            setUploading(false);
            setUploadProgress(0);
            e.target.value = '';
        }
    };

    const handleDelete = async (docId: number) => {
        if (!confirm('Are you sure you want to delete this document?')) return;

        try {
            await documentsService.delete(docId);
            await fetchDocuments();
        } catch (error) {
            alert('Failed to delete document');
        }
    };

    const getStatusIcon = (status: Document['status']) => {
        switch (status) {
            case 'completed':
                return <CheckCircle className="w-5 h-5 text-green-600" />;
            case 'processing':
                return <Loader className="w-5 h-5 text-blue-600 animate-spin" />;
            case 'failed':
                return <AlertCircle className="w-5 h-5 text-red-600" />;
            default:
                return <Loader className="w-5 h-5 text-gray-400 animate-spin" />;
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <Navbar />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-display font-bold text-gray-900 mb-2">
                        Document Management
                    </h1>
                    <p className="text-gray-600">Upload and manage your medical documents</p>
                </div>

                {/* Upload Section */}
                <div className="card mb-8">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-semibold text-gray-900">Upload Documents</h2>
                    </div>

                    <label className="block">
                        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-medical-blue transition-colors cursor-pointer">
                            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                            <p className="text-gray-700 font-medium mb-2">
                                Click to upload or drag and drop
                            </p>
                            <p className="text-sm text-gray-500">PDF files only</p>
                            <input
                                type="file"
                                multiple
                                accept=".pdf"
                                onChange={handleFileUpload}
                                disabled={uploading}
                                className="hidden"
                            />
                        </div>
                    </label>

                    {uploading && (
                        <div className="mt-4">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm text-gray-600">Uploading...</span>
                                <span className="text-sm font-semibold text-gray-900">{uploadProgress}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                                <div
                                    className="bg-medical-gradient h-2 rounded-full transition-all duration-300"
                                    style={{ width: `${uploadProgress}%` }}
                                ></div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Documents List */}
                <div className="card">
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">
                        Your Documents ({documents.length})
                    </h2>

                    {loading ? (
                        <div className="text-center py-12">
                            <Loader className="w-8 h-8 text-medical-blue animate-spin mx-auto" />
                        </div>
                    ) : documents.length === 0 ? (
                        <div className="text-center py-12">
                            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                            <p className="text-gray-600">No documents uploaded yet</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {documents.map((doc) => (
                                <div
                                    key={doc.id}
                                    className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-medical-blue transition-colors"
                                >
                                    <div className="flex items-center gap-4 flex-1">
                                        <FileText className="w-10 h-10 text-blue-600 flex-shrink-0" />
                                        <div className="flex-1 min-w-0">
                                            <h3 className="font-semibold text-gray-900 truncate">{doc.filename}</h3>
                                            <p className="text-sm text-gray-600">
                                                {formatFileSize(doc.file_size)} • {formatDate(doc.upload_date)}
                                            </p>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-3">
                                        <div className="flex items-center gap-2">
                                            {getStatusIcon(doc.status)}
                                            <span className="text-sm capitalize">{doc.status}</span>
                                        </div>

                                        <button
                                            onClick={() => handleDelete(doc.id)}
                                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                            title="Delete"
                                        >
                                            <Trash2 className="w-5 h-5" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default DocumentsPage;
