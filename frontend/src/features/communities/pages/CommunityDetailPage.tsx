import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { communitiesApi } from '@/shared/api';
import { formatDate } from '@/shared/lib/utils';
import { useAuth } from '@/features/auth/context/AuthContext';
import { ArrowLeft, Users, Crown, Calendar, Lock, Globe, Eye, UserPlus, Share2, FileText, TrendingUp, Clock, LogOut } from 'lucide-react';

const S = `
  @keyframes fadeUp { from { opacity:0; transform:translateY(16px); } to { opacity:1; transform:translateY(0); } }
  .tg-btn {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 10px 18px; border-radius: 10px; font-size: 14px; font-weight: 600;
    cursor: pointer; border: none; transition: all 0.2s; font-family: inherit;
  }
  .tg-btn-primary { background: #2196f3; color: #fff; }
  .tg-btn-primary:hover:not(:disabled) { background: #1e88e5; }
  .tg-btn-outline { background: transparent; color: #8ba4b8; border: 1.5px solid #2b3a4a; }
  .tg-btn-outline:hover:not(:disabled) { border-color: #2196f3; color: #2196f3; }
  .tg-btn-danger { background: transparent; color: #ef5350; border: 1.5px solid rgba(244,67,54,0.3); }
  .tg-btn-danger:hover:not(:disabled) { background: rgba(244,67,54,0.08); }
  .tg-btn:disabled { opacity: 0.45; cursor: not-allowed; }
  .tg-card { background: #1e2c3a; border: 1px solid #2b3a4a; border-radius: 14px; }
  .tg-row { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; border-radius: 10px; background: #17212b; }
`;

const visibilityConfig: Record<string, { label: string; color: string; bg: string; Icon: any }> = {
  public:  { label: 'Публичное',  color: '#4caf50', bg: 'rgba(76,175,80,0.1)',   Icon: Globe },
  private: { label: 'Приватное', color: '#ff9800', bg: 'rgba(255,152,0,0.1)',  Icon: Lock },
  secret:  { label: 'Секретное', color: '#f44336', bg: 'rgba(244,67,54,0.1)',  Icon: Eye },
};

export const CommunityDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const { data: community, isLoading } = useQuery({
    queryKey: ['community', id],
    queryFn: () => communitiesApi.get(id!),
    enabled: !!id,
  });

  const joinMutation = useMutation({
    mutationFn: () => communitiesApi.join(id!),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['community', id] }),
    onError: (e: any) => alert(e?.response?.data?.detail || 'Не удалось вступить'),
  });

  const leaveMutation = useMutation({
    mutationFn: () => communitiesApi.leave(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['community', id] });
    },
    onError: (e: any) => alert(e?.response?.data?.detail || 'Не удалось покинуть'),
  });

  if (isLoading) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', background: '#17212b' }}>
      <div style={{ width: '36px', height: '36px', border: '3px solid #2b3a4a', borderTop: '3px solid #2196f3', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );

  if (!community) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', background: '#17212b', fontFamily: 'inherit' }}>
      <div style={{ textAlign: 'center' }}>
        <p style={{ color: '#e8f0f8', fontSize: '18px', marginBottom: '16px' }}>Сообщество не найдено</p>
        <button className="tg-btn tg-btn-primary" onClick={() => navigate('/communities')}>
          <ArrowLeft size={16} /> Назад
        </button>
      </div>
    </div>
  );

  const vis = visibilityConfig[community.visibility] || visibilityConfig.public;
  const VisIcon = vis.Icon;
  const memberCount = community.members_count || 0;
  const postCount = community.posts_count || 0;
  const isOwner = community.is_owner || false;
  const isMember = community.is_member || false;
  const membershipStatus = community.membership_status;

  return (
    <div style={{
      minHeight: '100vh',
      background: '#17212b',
      fontFamily: "'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif",
      padding: '24px 20px',
      maxWidth: '760px',
      margin: '0 auto',
    }}>
      <style>{S}</style>

      {/* Back */}
      <button className="tg-btn tg-btn-outline" onClick={() => navigate('/communities')} style={{ marginBottom: '24px' }}>
        <ArrowLeft size={16} /> Назад
      </button>

      {/* Hero */}
      <div className="tg-card" style={{ padding: '28px', marginBottom: '16px', animation: 'fadeUp 0.3s ease' }}>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'flex-start', flexWrap: 'wrap' }}>
          {/* Avatar */}
          <div style={{
            width: '72px', height: '72px', borderRadius: '20px', flexShrink: 0,
            background: 'linear-gradient(135deg, #2196f3, #1565c0)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 8px 24px rgba(33,150,243,0.25)',
          }}>
            <Users size={32} color="#fff" />
          </div>

          <div style={{ flex: 1 }}>
            {/* Badge */}
            <span style={{
              display: 'inline-flex', alignItems: 'center', gap: '5px',
              padding: '4px 10px', borderRadius: '20px', fontSize: '12px', fontWeight: '600',
              color: vis.color, background: vis.bg, border: `1px solid ${vis.color}`,
              marginBottom: '10px',
            }}>
              <VisIcon size={12} /> {vis.label}
            </span>

            <h1 style={{ color: '#e8f0f8', fontSize: '22px', fontWeight: '700', margin: '0 0 8px' }}>
              {community.name}
            </h1>
            {community.description && (
              <p style={{ color: '#8ba4b8', fontSize: '14px', lineHeight: 1.6, margin: '0 0 16px' }}>
                {community.description}
              </p>
            )}

            {/* Actions */}
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              {isOwner ? (
                <Link to={`/posts/create?community=${id}`} className="tg-btn tg-btn-primary" style={{ textDecoration: 'none' }}>
                  <FileText size={16} /> Создать пост
                </Link>
              ) : isMember ? (
                membershipStatus === 'pending' ? (
                  <button className="tg-btn tg-btn-outline" disabled>
                    <Clock size={16} /> Ожидание
                  </button>
                ) : (
                  <button className="tg-btn tg-btn-danger" onClick={() => leaveMutation.mutate()} disabled={leaveMutation.isPending}>
                    <LogOut size={16} /> {leaveMutation.isPending ? 'Выход...' : 'Покинуть'}
                  </button>
                )
              ) : (
                <button className="tg-btn tg-btn-primary" onClick={() => joinMutation.mutate()} disabled={joinMutation.isPending || !user}>
                  <UserPlus size={16} /> {joinMutation.isPending ? 'Вступление...' : 'Вступить'}
                </button>
              )}
              <button className="tg-btn tg-btn-outline">
                <Share2 size={16} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '16px' }}>
        {[
          { icon: Users, value: memberCount, label: 'Участников', color: '#2196f3' },
          { icon: FileText, value: postCount, label: 'Постов', color: '#9c27b0' },
          { icon: TrendingUp, value: `+${Math.floor(memberCount * 0.15)}`, label: 'За месяц', color: '#4caf50' },
        ].map(({ icon: Icon, value, label, color }) => (
          <div key={label} className="tg-card" style={{ padding: '18px', animation: 'fadeUp 0.35s ease' }}>
            <div style={{ color, marginBottom: '8px' }}><Icon size={20} /></div>
            <div style={{ color: '#e8f0f8', fontSize: '22px', fontWeight: '700' }}>{value}</div>
            <div style={{ color: '#4a6278', fontSize: '12px', marginTop: '2px' }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Owner */}
      <div className="tg-card" style={{ padding: '20px', marginBottom: '16px' }}>
        <div style={{ color: '#8ba4b8', fontSize: '11px', fontWeight: '700', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Crown size={13} color="#ffc107" /> Владелец
        </div>
        <Link to={`/profile/${community.owner || ''}`} style={{ display: 'flex', alignItems: 'center', gap: '14px', textDecoration: 'none' }}>
          <div style={{
            width: '44px', height: '44px', borderRadius: '50%', flexShrink: 0,
            background: 'linear-gradient(135deg, #ffc107, #ff9800)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: '#fff', fontWeight: '700', fontSize: '18px',
          }}>
            {community.owner_username?.[0]?.toUpperCase() || 'O'}
          </div>
          <div>
            <div style={{ color: '#e8f0f8', fontWeight: '600', fontSize: '15px' }}>{community.owner_username}</div>
            <div style={{ color: '#4a6278', fontSize: '12px' }}>Основатель</div>
          </div>
        </Link>
      </div>

      {/* Info */}
      <div className="tg-card" style={{ padding: '20px', marginBottom: '16px' }}>
        <div style={{ color: '#8ba4b8', fontSize: '11px', fontWeight: '700', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: '14px' }}>
          Информация
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div className="tg-row">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#4a6278', fontSize: '14px' }}>
              <Calendar size={15} /> Создано
            </div>
            <span style={{ color: '#e8f0f8', fontSize: '14px', fontWeight: '500' }}>{formatDate(community.created_at)}</span>
          </div>
          <div className="tg-row">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#4a6278', fontSize: '14px' }}>
              <VisIcon size={15} /> Видимость
            </div>
            <span style={{ color: '#e8f0f8', fontSize: '14px', fontWeight: '500' }}>{vis.label}</span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="tg-card" style={{ padding: '20px' }}>
        <div style={{ color: '#8ba4b8', fontSize: '11px', fontWeight: '700', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: '14px' }}>
          Действия
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <Link to={`/posts?community=${id}`} className="tg-btn tg-btn-outline" style={{ textDecoration: 'none', justifyContent: 'flex-start' }}>
            <FileText size={16} /> Посты ({postCount})
          </Link>
          <button className="tg-btn tg-btn-outline" style={{ justifyContent: 'flex-start' }}
            onClick={async () => {
              try {
                const members = await communitiesApi.getMembers(id!);
                alert(members.length === 0
                  ? 'Участников: 0'
                  : `Участников: ${members.length}\n\n${members.map((m: any) => `${m.user_username} (${m.role === 'organizer' ? 'Владелец' : m.role === 'moderator' ? 'Модератор' : 'Участник'})`).join('\n')}`
                );
              } catch (e: any) { alert(e?.response?.data?.detail || 'Ошибка'); }
            }}>
            <Users size={16} /> Участники ({memberCount})
          </button>
          <button className="tg-btn tg-btn-outline" style={{ justifyContent: 'flex-start', opacity: 0.45, cursor: 'not-allowed' }} disabled>
            <Share2 size={16} /> Пригласить (скоро)
          </button>
        </div>
      </div>
    </div>
  );
};