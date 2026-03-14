import { NavLink, useLocation } from 'react-router-dom';
import { Home, FileText, Calendar, Users, Bell, User } from 'lucide-react';
import { cn } from '@/shared/lib/utils';
import { useAuth } from '@/features/auth/context/AuthContext';

const navItems = [
  { to: '/', icon: Home, label: 'Главная' },
  { to: '/posts', icon: FileText, label: 'Посты' },
  { to: '/events', icon: Calendar, label: 'События' },
  { to: '/communities', icon: Users, label: 'Сообщества' },
  { to: '/notifications', icon: Bell, label: 'Уведомления' },
  { to: '/profile', icon: User, label: 'Профиль', isProfile: true },
];

export const Sidebar = () => {
  const location = useLocation();
  const { user } = useAuth();

  const isProfileActive = (item: typeof navItems[0]) => {
    if (!item.isProfile) return false;
    
    if (location.pathname === '/profile') {
      return true;
    }
    
    const profileMatch = location.pathname.match(/^\/profile\/(.+)$/);
    if (profileMatch) {
      const userId = profileMatch[1];
      return user?.id === userId;
    }
    
    return false;
  };

  return (
    <aside className="w-64 border-r bg-muted/40 p-4">
      <nav className="space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = item.isProfile 
            ? isProfileActive(item)
            : location.pathname === item.to || location.pathname.startsWith(item.to + '/');
          
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={cn(
                'flex items-center space-x-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground'
              )}
            >
              <Icon className="h-5 w-5" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
};

