import api from './api';

export interface UsageOverview {
    total_documents: number;
    total_queries: number;
    total_tokens: number;
    avg_response_time: number;
}

export interface UsageDataPoint {
    date: string;
    queries: number;
    documents: number;
}

export interface UsageGraphData {
    data_points: UsageDataPoint[];
    period: string;
}

export interface TopicData {
    topic: string;
    count: number;
}

export interface TopTopics {
    topics: TopicData[];
}

const analyticsService = {
    getOverview: async (): Promise<UsageOverview> => {
        const response = await api.get<UsageOverview>('/api/v1/analytics/overview');
        return response.data;
    },

    getUsageGraph: async (period: 'daily' | 'weekly' = 'daily'): Promise<UsageGraphData> => {
        const response = await api.get<UsageGraphData>('/api/v1/analytics/usage-graph', {
            params: { period },
        });
        return response.data;
    },

    getTopTopics: async (limit: number = 5): Promise<TopTopics> => {
        const response = await api.get<TopTopics>('/api/v1/analytics/top-topics', {
            params: { limit },
        });
        return response.data;
    },
};

export default analyticsService;
