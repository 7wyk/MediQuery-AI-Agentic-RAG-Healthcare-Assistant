import api from './api';

export interface Document {
    id: number;
    filename: string;
    file_size: number;
    upload_date: string;
    status: 'uploading' | 'processing' | 'completed' | 'failed';
    error_message?: string;
}

export interface DocumentListResponse {
    documents: Document[];
    total: number;
}

const documentsService = {
    upload: async (files: FileList, onProgress?: (progress: number) => void): Promise<Document[]> => {
        const formData = new FormData();
        Array.from(files).forEach((file) => {
            formData.append('files', file);
        });

        const response = await api.post<Document[]>('/api/v1/documents/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            onUploadProgress: (progressEvent) => {
                if (onProgress && progressEvent.total) {
                    const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    onProgress(progress);
                }
            },
        });

        return response.data;
    },

    list: async (): Promise<DocumentListResponse> => {
        const response = await api.get<DocumentListResponse>('/api/v1/documents');
        return response.data;
    },

    getStatus: async (docId: number): Promise<Document> => {
        const response = await api.get<Document>(`/api/v1/documents/${docId}/status`);
        return response.data;
    },

    delete: async (docId: number): Promise<void> => {
        await api.delete(`/api/v1/documents/${docId}`);
    },

    reindex: async (docId: number): Promise<void> => {
        await api.post(`/api/v1/documents/${docId}/reindex`);
    },
};

export default documentsService;
