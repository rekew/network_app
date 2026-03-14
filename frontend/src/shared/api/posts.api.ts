import { apiClient } from '@/shared/lib/api';
import type { Post, Comment, CreatePostRequest, PaginatedResponse } from '@/shared/types';

export const postsApi = {
  list: (params?: { community?: string; search?: string }): Promise<Post[] | PaginatedResponse<Post>> =>
    apiClient.get('/posts/', { params }),

  get: (id: string): Promise<Post> =>
    apiClient.get(`/posts/${id}/`),

  create: (data: CreatePostRequest): Promise<Post> =>
    apiClient.post('/posts/', data),

  update: (id: string, data: Partial<CreatePostRequest>): Promise<Post> =>
    apiClient.put(`/posts/${id}/`, data),

  delete: (id: string, token: string) => 
  apiClient.delete(`/posts/${id}/`, {
    headers: { Authorization: `Bearer ${token}` }
  }),

  getUserPosts: (userId: string): Promise<Post[]> =>
    apiClient.get(`/posts/?user=${userId}`),

  // Comments 
  getComments: async (postId: string): Promise<Comment[]> => {
    try {
      return await apiClient.get<Comment[]>(`/comments/?post=${postId}`);
    } catch {
      return [];
    }
  },

  createComment: async (postId: string, data: { content: string }): Promise<Comment> =>
    apiClient.post(`/comments/`, { ...data, post: postId }),

  // Likes
  like: async (postId: string): Promise<Post> =>
    apiClient.post(`/${postId}/like/`, {}),

  unlike: async (postId: string): Promise<Post> =>
    apiClient.delete(`/${postId}/like/`),
};