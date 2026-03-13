import { apiClient } from '@/shared/lib/api';
import type { Community, CommunityMembership, CreateCommunityRequest, PaginatedResponse } from '@/shared/types';

export const communitiesApi = {
  list: (params?: { visibility?: string; search?: string }): Promise<Community[] | PaginatedResponse<Community>> =>
    apiClient.get('/communities/api/', { params }),

  get: (id: string): Promise<Community> =>
    apiClient.get(`/communities/api/${id}/`),

  create: (data: CreateCommunityRequest): Promise<Community> =>
    apiClient.post('/communities/api/', data),

  update: (id: string, data: Partial<CreateCommunityRequest>): Promise<Community> =>
    apiClient.put(`/communities/api/${id}/`, data),

  delete: (id: string): Promise<void> =>
    apiClient.delete(`/communities/api/${id}/`),

  join: (id: string): Promise<CommunityMembership> =>
    apiClient.post(`/communities/api/${id}/join/`),

  leave: (id: string): Promise<void> =>
    apiClient.post(`/communities/api/${id}/leave/`),

  getMembers: (id: string): Promise<CommunityMembership[]> =>
    apiClient.get(`/communities/api/${id}/members/`),
};