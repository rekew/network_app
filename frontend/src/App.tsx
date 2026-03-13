import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './features/auth/context/AuthContext';
import { ProtectedRoute } from './features/auth/components/ProtectedRoute';
import { LoginPage } from './features/auth/pages/LoginPage';
import { RegisterPage } from './features/auth/pages/RegisterPage';
import { DashboardPage } from './features/dashboard/pages/DashboardPage';
import { Layout } from './widgets/layout/Layout';
import { PostsListPage } from './features/posts/pages/PostsListPage';
import { PostDetailPage } from './features/posts/pages/PostDetailPage';
import { CreatePostPage } from './features/posts/pages/CreatePostPage';
import { CommunitiesListPage } from './features/communities/pages/CommunitiesListPage';
import { CommunityDetailPage } from './features/communities/pages/CommunityDetailPage';
import { CreateCommunityPage } from './features/communities/pages/CreateCommunityPage';
import { ProfilePage } from './features/users/pages/ProfilePage';
import { NotificationsPage } from './features/notifications/pages/NotificationsPage';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<DashboardPage />} />
            <Route path="posts" element={<PostsListPage />} />
            <Route path="posts/create" element={<CreatePostPage />} />
            <Route path="posts/:id" element={<PostDetailPage />} />
            <Route path="communities" element={<CommunitiesListPage />} />
            <Route path="communities/create" element={<CreateCommunityPage />} />
            <Route path="communities/:id" element={<CommunityDetailPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="profile/:userId" element={<ProfilePage />} />
            <Route path="notifications" element={<NotificationsPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;

