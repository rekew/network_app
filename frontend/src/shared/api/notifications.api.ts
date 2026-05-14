import { apiClient } from '@/shared/lib/api';
import type { Notification, PaginatedResponse } from '@/shared/types';

export const notificationsApi = {
  list: (): Promise<Notification[] | PaginatedResponse<Notification>> =>
    apiClient.get('/notifications/notifications/'),

  markAsRead: (id: string): Promise<Notification> =>
    apiClient.patch(`/notifications/notifications/${id}/`),
};

