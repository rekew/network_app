import { apiClient } from '@/shared/lib/api';
import type { User, Profile, PaginatedResponse } from '@/shared/types';

export const usersApi = {
  list: async (): Promise<User[] | PaginatedResponse<User>> =>
    await apiClient.get('/api/users/'),

  get: async (id: string | number): Promise<User> =>
    await apiClient.get(`/api/users/${id}/`),

  update: async (id: string | number, data: Partial<User>): Promise<User> =>
    await apiClient.patch(`/api/users/${id}/update/`, data),

  delete: async (id: string | number): Promise<void> =>
    await apiClient.delete(`/api/users/${id}/delete/`),

  // Profiles
  getProfile: async (id: string | number): Promise<Profile> =>
    await apiClient.get(`/api/profiles/${id}/`),

  updateProfile: async (id: string | number, data: Partial<Profile> | FormData): Promise<Profile> => {
    if (data instanceof FormData) {
      return await apiClient.patch(`/api/profiles/${id}/update/`, data);
    }
    return await apiClient.patch(`/api/profiles/${id}/update/`, data);
  },

  deleteProfile: async (id: string | number): Promise<void> =>
    await apiClient.delete(`/api/profiles/${id}/delete/`),

  // Friendships
  getFriendships: async (): Promise<any[]> =>
    await apiClient.get('/api/friendships/'),

  createFriendship: async (data: { friend_id: number }): Promise<any> =>
    await apiClient.post('/api/friendships/create/', data),

  deleteFriendship: async (id: string | number): Promise<void> =>
    await apiClient.delete(`/api/friendships/${id}/delete/`),

  // User blocks
  getBlocks: async (): Promise<any[]> =>
    await apiClient.get('/api/user-blocks/'),

  blockUser: async (data: { blocked_id: number }): Promise<any> =>
    await apiClient.post('/api/user-blocks/create/', data),

  unblockUser: async (id: string | number): Promise<void> =>
    await apiClient.delete(`/api/user-blocks/${id}/delete/`),

  // Activity logs
  getActivityLogs: async (): Promise<any[]> =>
    await apiClient.get('/api/activity-logs/'),

  createActivityLog: async (data: any): Promise<any> =>
    await apiClient.post('/api/activity-logs/create/', data),

  // Reports
  getReports: async (): Promise<any[]> =>
    await apiClient.get('/api/reports/'),

  getReport: async (id: string | number): Promise<any> =>
    await apiClient.get(`/api/reports/${id}/`),

  createReport: async (data: any): Promise<any> =>
    await apiClient.post('/api/reports/create/', data),
};