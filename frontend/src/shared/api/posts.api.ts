import { apiClient } from '@/shared/lib/api';
import type { Post, Comment, CreatePostRequest, PaginatedResponse } from '@/shared/types';

export const postsApi = {
  list: (params?: { community?: string; search?: string }): Promise<Post[] | PaginatedResponse<Post>> =>
    apiClient.get('/posts/posts/', { params }),

  get: (id: string): Promise<Post> =>
    apiClient.get(`/posts/posts/${id}/`),

  create: (data: CreatePostRequest): Promise<Post> =>
    apiClient.post('/posts/posts/', data),

  update: (id: string, data: Partial<CreatePostRequest>): Promise<Post> =>
    apiClient.put(`/posts/posts/${id}/`, data),

  delete: (id: string): Promise<void> =>
    apiClient.delete(`/posts/posts/${id}/`),

  getUserPosts: (userId: string): Promise<Post[]> =>
    apiClient.get(`/posts/posts/?user=${userId}`),

  // Comments 
  getComments: async (postId: string): Promise<Comment[]> => {
    try {
      return await apiClient.get<Comment[]>(`/posts/comments/?post=${postId}`);
    } catch {
      return [];
    }
  },

  createComment: async (postId: string, data: { content: string }): Promise<Comment> =>
    apiClient.post(`/posts/comments/`, { ...data, post: postId }),

  // Likes
  like: async (postId: string): Promise<Post> =>
    apiClient.post(`/posts/posts/${postId}/like/`, {}),

  unlike: async (postId: string): Promise<Post> =>
    apiClient.delete(`/posts/posts/${postId}/like/`),
};