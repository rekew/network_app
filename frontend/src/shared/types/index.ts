// Base types
export interface BaseModel {
  id: string;
  created_at: string;
  updated_at?: string;
  deleted_at?: string | null;
}

// User types
export interface User extends BaseModel {
  username: string;
  email: string;
  full_name?: string;
  first_name?: string;
  last_name?: string;
  phone_number?: string;
  city?: string;
  country?: string;
  birthdate?: string;
  is_active: boolean;
  is_staff: boolean;
  date_joined: string;
  last_login?: string;
  profile?: Profile;
}

export interface Profile {
  id: number;
  user: string;
  display_name?: string;
  bio?: string;
  location?: string;
  interests: string[];
  is_verified: boolean;
  avatar?: string;
  gender: 'male' | 'female' | 'other';
  updated_at: string;
}

export interface UserWithProfile extends User {
  profile?: Profile;
}

// Auth types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  full_name: string;
  password: string;
}

export interface AuthResponse {
  id: string;
  email: string;
  access: string;
  refresh: string;
}

// Post types
export interface Tag {
  id: string;
  name: string;
}

export interface Post extends BaseModel {
  author: string;
  author_username: string;
  community?: string;
  community_slug?: string;
  community_name?: string;
  content: string;
  pinned: boolean;
  tags: Tag[];
  likes_count?: number;
  is_liked?: boolean;
  liked_by?: Array<{ id: string; username: string }>;
  comment_authors?: Array<{ id: string; username: string }>;
  edited_at?: string;
  can_edit?: boolean;
  is_author?: boolean;
}

export interface Comment extends BaseModel {
  post: string;
  author: string;
  author_username: string;
  parent?: string;
  content: string;
}

export interface CreatePostRequest {
  content: string;
  community?: string;
  tags?: string[];
}

export interface CreateCommentRequest {
  post: string;
  content: string;
  parent?: string;
}

// Community types
export interface Community extends BaseModel {
  posts_count: number;
  members_count: number;
  category: any;
  name: string;
  slug: string;
  description?: string;
  visibility: 'public' | 'private' | 'secret';
  owner: string;
  owner_username: string;
  is_owner?: boolean;
  is_member?: boolean;
  membership_role?: 'member' | 'moderator' | 'organizer' | null;
  membership_status?: 'pending' | 'active' | 'banned' | null;
}

export interface CommunityMembership {
  id: string;
  user: string;
  user_username: string;
  community: string;
  community_name: string;
  role: 'member' | 'moderator' | 'organizer';
  status: 'pending' | 'active' | 'banned';
  joined_at: string;
}

export interface CreateCommunityRequest {
  name: string;
  description?: string;
  visibility?: 'public' | 'private' | 'secret';
}

// Event types
export interface Event {
  location: any;
  id: string;
  title: string;
  description: string;
  start_at: string;
  end_at: string;
  capacity?: number;
  status: 'draft' | 'published' | 'cancelled';
  organizer: string;
  organizer_username: string;
  community: string;
  community_slug: string;
  requires_approval: boolean;
  questions: any[];
}

export interface EventApplication {
  id: string;
  event: string;
  event_title: string;
  user: string;
  user_username: string;
  status: 'applied' | 'pending' | 'approved' | 'declined' | 'cancelled';
  answers: Record<string, any>;
  applied_at: string;
  reviewed_at?: string;
  reviewed_by?: string;
}

export interface CreateEventRequest {
  title: string;
  description: string;
  start_at: string;
  end_at: string;
  capacity?: number;
  status?: 'draft' | 'published' | 'cancelled';
  community: string;
  requires_approval?: boolean;
  questions?: any[];
}

export interface ApplyToEventRequest {
  answers?: Record<string, any>;
}

// Notification types
export interface Notification extends BaseModel {
  user: string;
  type?: 'comment' | 'like' | 'follow' | 'event' | 'community' | 'post';
  title?: string;
  message: string;
  is_read?: boolean;
  link?: string;
  related_object_id?: string;
  related_object_type?: string;
}

// Report types
export interface Report {
  id: string;
  reporter: string;
  reason: string;
  status: string;
  handled_by?: string;
}

// Media types
export interface Media extends BaseModel {
  owner: string;
  media_type: 'image' | 'video' | 'file';
  file: string;
  title?: string;
  description?: string;
}

// API Response types
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  detail?: string;
  message?: string;
  [key: string]: any;
}

