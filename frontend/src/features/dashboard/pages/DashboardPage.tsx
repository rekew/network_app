import { FileText, Calendar, Users, TrendingUp, Plus, ArrowRight, Clock, MessagesSquare } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { postsApi, communitiesApi } from '@/shared/api';
import { formatDate } from '@/shared/lib/utils';

const S = `
  @keyframes fadeUp { from { opacity:0; transform:translateY(14px); } to { opacity:1; transform:translateY(0); } }
  .tg-card { background:#1e2c3a; border:1px solid #2b3a4a; border-radius:14px; }
  .tg-post-row {
    display:flex; align-items:flex-start; gap:12px; padding:12px 14px;
    border-radius:10px; background:#17212b; transition:background 0.15s;
    text-decoration:none; color:inherit;
  }
  .tg-post-row:hover { background:#1a2733; }
  .tg-action-btn {
    display:flex; align-items:center; gap:8px; padding:11px 14px;
    border-radius:10px; font-size:14px; font-weight:600; cursor:pointer;
    transition:all 0.2s; text-decoration:none; border:none; font-family:inherit; width:100%; box-sizing:border-box;
  }
  .tg-action-primary { background:#2196f3; color:#fff; }
  .tg-action-primary:hover { background:#1e88e5; }
  .tg-action-outline { background:transparent; color:#8ba4b8; border:1.5px solid #2b3a4a; }
  .tg-action-outline:hover { border-color:#2196f3; color:#2196f3; }
  .tg-event-row {
    display:block; padding:12px 14px; border-radius:10px; background:#17212b;
    transition:background 0.15s; text-decoration:none; color:inherit;
  }
  .tg-event-row:hover { background:#1a2733; }
  @media (max-width: 700px) { .main-grid { grid-template-columns: 1fr !important; } }
`;

export const DashboardPage = () => {
  const { data: postsData } = useQuery({ queryKey: ['posts'], queryFn: () => postsApi.list() });
  const { data: communitiesData } = useQuery({ queryKey: ['communities'], queryFn: () => communitiesApi.list() });

  const posts = Array.isArray(postsData) ? postsData : (postsData as any)?.results || [];
  const communities = Array.isArray(communitiesData) ? communitiesData : (communitiesData as any)?.results || [];

  const recentPosts = posts.slice(0, 4);
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const todayActivity = posts.filter((p: any) => new Date(p.created_at) >= today).length;

  const stats = [
    { label: 'Посты', value: posts.length, icon: FileText, color: '#2196f3' },
    { label: 'Сообщества', value: communities.length, icon: Users, color: '#4caf50' },
    { label: 'Сегодня', value: todayActivity, icon: TrendingUp, color: '#ff9800' },
  ];
  const upcomingEvents: any[] = [];

  return (
    <div style={{ minHeight: '100vh', background: '#17212b', fontFamily: "'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif", padding: '24px 20px', maxWidth: '1000px', margin: '0 auto' }}>
      <style>{S}</style>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '28px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ color: '#e8f0f8', fontSize: '26px', fontWeight: '700', margin: '0 0 4px' }}>Главная</h1>
          <p style={{ color: '#4a6278', fontSize: '14px', margin: 0 }}>Добро пожаловать в Hubbly</p>
        </div>
        <Link to="/posts/create" className="tg-action-btn tg-action-primary" style={{ width: 'auto', padding: '10px 18px' }}>
          <Plus size={16} /> Создать пост
        </Link>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', marginBottom: '24px' }}>
        {stats.map(({ label, value, icon: Icon, color }, i) => (
          <div key={label} className="tg-card" style={{ padding: '20px', animation: `fadeUp 0.3s ease ${i * 60}ms both` }}>
            <div style={{ color, marginBottom: '10px' }}><Icon size={20} /></div>
            <div style={{ color: '#e8f0f8', fontSize: '28px', fontWeight: '700', lineHeight: 1 }}>{value}</div>
            <div style={{ color: '#4a6278', fontSize: '12px', marginTop: '4px' }}>{label}</div>
          </div>
        ))}
      </div>

      <div className="main-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: '16px', alignItems: 'start' }}>
        <div className="tg-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div>
              <div style={{ color: '#e8f0f8', fontSize: '16px', fontWeight: '700' }}>Последние посты</div>
              <div style={{ color: '#4a6278', fontSize: '12px', marginTop: '2px' }}>Свежий контент</div>
            </div>
            <Link to="/posts" style={{ color: '#2196f3', fontSize: '13px', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px' }}>
              Все <ArrowRight size={14} />
            </Link>
          </div>
          {recentPosts.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <MessagesSquare size={36} color="#2b3a4a" style={{ marginBottom: '12px' }} />
              <p style={{ color: '#4a6278', fontSize: '14px', marginBottom: '16px' }}>Пока нет постов</p>
              <Link to="/posts/create" className="tg-action-btn tg-action-primary" style={{ width: 'auto', display: 'inline-flex', padding: '10px 18px' }}>
                Создать первый пост
              </Link>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {recentPosts.map((post: any) => (
                <Link key={post.id} to={`/posts/${post.id}`} className="tg-post-row">
                  <div style={{ width: '38px', height: '38px', borderRadius: '50%', flexShrink: 0, background: 'linear-gradient(135deg, #2196f3, #1565c0)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: '700', fontSize: '15px' }}>
                    {post.author_username?.[0]?.toUpperCase() || 'U'}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '3px' }}>
                      <span style={{ color: '#e8f0f8', fontWeight: '600', fontSize: '13px' }}>{post.author_username}</span>
                      <span style={{ color: '#4a6278', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '3px' }}>
                        <Clock size={10} /> {formatDate(post.created_at)}
                      </span>
                    </div>
                    <p style={{ color: '#8ba4b8', fontSize: '13px', margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {post.content?.split('\n')[0]?.slice(0, 100)}
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div className="tg-card" style={{ padding: '18px' }}>
            <div style={{ color: '#8ba4b8', fontSize: '11px', fontWeight: '700', letterSpacing: '0.07em', textTransform: 'uppercase', marginBottom: '12px' }}>Быстрые действия</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <Link to="/posts/create" className="tg-action-btn tg-action-primary"><Plus size={15} /> Создать пост</Link>
              <Link to="/events" className="tg-action-btn tg-action-outline"><Calendar size={15} /> События</Link>
              <Link to="/communities" className="tg-action-btn tg-action-outline"><Users size={15} /> Сообщества</Link>
            </div>
          </div>

          <div className="tg-card" style={{ padding: '18px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <div style={{ color: '#8ba4b8', fontSize: '11px', fontWeight: '700', letterSpacing: '0.07em', textTransform: 'uppercase' }}>Предстоящие</div>
              <Link to="/events" style={{ color: '#2196f3', fontSize: '12px', textDecoration: 'none' }}>Все</Link>
            </div>
            {upcomingEvents.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '20px 0' }}>
                <Calendar size={28} color="#2b3a4a" style={{ marginBottom: '8px' }} />
                <p style={{ color: '#4a6278', fontSize: '13px', margin: 0 }}>Нет событий</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {upcomingEvents.map((event: any) => (
                  <Link key={event.id} to={`/events/${event.id}`} className="tg-event-row">
                    <div style={{ color: '#e8f0f8', fontWeight: '600', fontSize: '13px', marginBottom: '3px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{event.title}</div>
                    <div style={{ color: '#4a6278', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '4px' }}><Calendar size={10} /> {formatDate(event.start_at)}</div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};