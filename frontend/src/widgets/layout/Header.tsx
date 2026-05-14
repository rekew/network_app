import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/features/auth/context/AuthContext';
import { Button } from '@/shared/components/ui/button';
import { Bell } from 'lucide-react';

export const Header = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center space-x-2">
          <span className="text-2xl font-bold text-primary">Hubbly</span>
        </Link>

        <nav className="flex items-center space-x-6">
          <Link to="/notifications" className="relative">
            <Bell className="h-5 w-5" />
          </Link>
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium">{user?.full_name || user?.username || user?.email}</span>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              Выход
            </Button>
          </div>
        </nav>
      </div>
    </header>
  );
};

