import api from './api';

export interface ChatQuery {
    question: string;
    language?: string;
    mode?: 'standard' | 'agentic';
}

export interface SourceDocument {
    content: string;
    metadata: Record<string, any>;
    relevance_score?: number;
}

export interface AgentMetadata {
    retrieval_attempts: number;
    retrieval_refined: boolean;
    documents_retrieved: number;
    relevance_score: number;
    steps: string[];
    fallback_to_standard: boolean;
}

export interface ChatResponse {
    answer: string;
    sources: SourceDocument[];
    response_time: number;
    language: string;
    mode?: string;
    agent_metadata?: AgentMetadata | null;
}

export interface ChatHistoryItem {
    id: number;
    question: string;
    answer: string;
    timestamp: string;
    language: string;
}

export interface ChatHistoryResponse {
    history: ChatHistoryItem[];
    total: number;
}

const chatService = {
    query: async (data: ChatQuery): Promise<ChatResponse> => {
        const response = await api.post<ChatResponse>('/api/v1/chat/query', data);
        return response.data;
    },

    queryMultilang: async (data: ChatQuery): Promise<ChatResponse> => {
        const response = await api.post<ChatResponse>('/api/v1/chat/query-multilang', data);
        return response.data;
    },

    getHistory: async (limit: number = 50): Promise<ChatHistoryResponse> => {
        const response = await api.get<ChatHistoryResponse>('/api/v1/chat/history', {
            params: { limit },
        });
        return response.data;
    },

    clearHistory: async (): Promise<void> => {
        await api.delete('/api/v1/chat/history');
    },
};

export default chatService;
