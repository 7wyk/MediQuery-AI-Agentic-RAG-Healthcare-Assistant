import api from './api';

export interface RegisterData {
    email: string;
    password: string;
    full_name: string;
    role: 'doctor' | 'student';
}

export interface LoginData {
    email: string;
    password: string;
}

export interface AuthResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
}

export interface User {
    id: number;
    email: string;
    full_name: string;
    role: 'doctor' | 'student';
    created_at: string;
}

const authService = {
    register: async (data: RegisterData): Promise<User> => {
        const response = await api.post<User>('/api/v1/auth/register', data);
        return response.data;
    },

    login: async (data: LoginData): Promise<AuthResponse> => {
        const response = await api.post<AuthResponse>('/api/v1/auth/login', data);
        const { access_token, refresh_token } = response.data;

        // Store tokens
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);

        return response.data;
    },

    logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    },

    getCurrentUser: async (): Promise<User> => {
        const response = await api.get<User>('/api/v1/auth/me');
        return response.data;
    },

    isAuthenticated: (): boolean => {
        return !!localStorage.getItem('access_token');
    },
};

export default authService;
