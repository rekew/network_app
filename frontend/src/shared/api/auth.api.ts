import { apiClient } from '@/shared/lib/api';
import type { AuthResponse, LoginRequest, RegisterRequest, User } from '@/shared/types';

// Decode JWT payload to get user_id
const decodeToken = (token: string): { user_id: number } | null => {
  try {
    const payload = token.split('.')[1];
    return JSON.parse(atob(payload));
  } catch {
    return null;
  }
};

export const authApi = {
  register: (data: RegisterRequest): Promise<AuthResponse> =>
    apiClient.post('/api/auth/register/', data),

  login: (data: LoginRequest): Promise<AuthResponse> =>
    apiClient.post('/api/auth/login/', data),

  verifyToken: (token: string): Promise<{ detail?: string }> =>
    apiClient.post('/api/token/verify/', { token }),

  refreshToken: (refresh: string): Promise<{ access: string }> =>
    apiClient.post('/api/token/refresh/', { refresh }),

  getCurrentUser: (accessToken: string): Promise<User> => {
    const decoded = decodeToken(accessToken);
    if (!decoded?.user_id) return Promise.reject(new Error('Invalid token'));
    return apiClient.get(`/api/users/${decoded.user_id}/`);
  },
};