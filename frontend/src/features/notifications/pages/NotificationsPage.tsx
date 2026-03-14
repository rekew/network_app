import { useQuery } from '@tanstack/react-query';
import { notificationsApi } from '@/shared/api';
import { formatDate } from '@/shared/lib/utils';
import { Bell, BellOff, Check, MessageSquare, Heart, UserPlus, Calendar, Trash2 } from 'lucide-react';

const S = `
  @keyframes fadeUp { from { opacity:0; transform:translateY(14px); } to { opacity:1; transform:translateY(0); } }
  @keyframes spin { to { transform:rotate(360deg); } }
  .tg-card { background:#1e2c3a; border:1px solid #2b3a4a; border-radius:14px; }
  .tg-notif { display:flex; align-items:flex-start; gap:14px; padding:16px; border-radius:12px; border:1px solid #2b3a4a; background:#1e2c3a; transition:border-color 0.2s; }
  .tg-notif.unread { border-color:#2196f330; }
  .tg-icon-btn { display:inline-flex; align-items:center; justify-content:center; width:32px; height:32px; border-radius:8px; border:none; cursor:pointer; transition:all 0.2s; background:transparent; }
  .tg-icon-btn:hover { background:#242f3d; }
  .tg-icon-btn.danger:hover { background:rgba(244,67,54,0.1); }
`;

const iconConfig: Record<string, { Icon: any; color: string; bg: string }> = {
  comment: { Icon: MessageSquare, color: '#2196f3', bg: 'rgba(33,150,243,0.15)' },
  like:    { Icon: Heart,         color: '#f44336', bg: 'rgba(244,67,54,0.15)' },
  follow:  { Icon: UserPlus,      color: '#4caf50', bg: 'rgba(76,175,80,0.15)' },
  event:   { Icon: Calendar,      color: '#9c27b0', bg: 'rgba(156,39,176,0.15)' },
};
const getIcon = (type: string) => iconConfig[type] || { Icon: Bell, color: '#8ba4b8', bg: 'rgba(138,164,184,0.15)' };
const typeLabel: Record<string, string> = { comment: 'Комментарий', like: 'Лайк', follow: 'Подписка', event: 'Событие', community: 'Сообщество', post: 'Пост' };

export const NotificationsPage = () => {
  const { data: notifications, isLoading } = useQuery({ queryKey: ['notifications'], queryFn: () => notificationsApi.list() });
  const list = Array.isArray(notifications) ? notifications : (notifications as any)?.results || [];
  const unreadCount = list.filter((n: any) => !n.is_read).length;

  if (isLoading) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', background: '#17212b' }}>
      <div style={{ width: '36px', height: '36px', border: '3px solid #2b3a4a', borderTop: '3px solid #2196f3', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );

  return (
    <div style={{ minHeight: '100vh', background: '#17212b', fontFamily: "'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif", padding: '24px 20px', maxWidth: '700px', margin: '0 auto' }}>
      <style>{S}</style>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '28px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ color: '#e8f0f8', fontSize: '26px', fontWeight: '700', margin: '0 0 4px' }}>Уведомления</h1>
          <p style={{ color: '#4a6278', fontSize: '14px', margin: 0 }}>
            {list.length > 0 ? `${list.length} уведомлений` : 'Нет уведомлений'}
            {unreadCount > 0 && <span style={{ marginLeft: '8px', padding: '2px 8px', background: 'rgba(33,150,243,0.15)', color: '#2196f3', borderRadius: '20px', fontSize: '12px', fontWeight: '600' }}>{unreadCount} новых</span>}
          </p>
        </div>
        {list.length > 0 && (
          <button style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '10px 16px', borderRadius: '10px', background: 'transparent', border: '1.5px solid #2b3a4a', color: '#8ba4b8', fontSize: '13px', fontWeight: '600', cursor: 'pointer', fontFamily: 'inherit' }}>
            <Check size={15} /> Прочитать все
          </button>
        )}
      </div>

      {list.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', marginBottom: '24px' }}>
          {[
            { label: 'Всего', value: list.length, Icon: Bell, color: '#2196f3' },
            { label: 'Прочитано', value: list.length - unreadCount, Icon: Check, color: '#4caf50' },
            { label: 'Новых', value: unreadCount, Icon: BellOff, color: '#ff9800' },
          ].map(({ label, value, Icon, color }) => (
            <div key={label} className="tg-card" style={{ padding: '16px' }}>
              <div style={{ color, marginBottom: '8px' }}><Icon size={18} /></div>
              <div style={{ color: '#e8f0f8', fontSize: '22px', fontWeight: '700' }}>{value}</div>
              <div style={{ color: '#4a6278', fontSize: '12px', marginTop: '2px' }}>{label}</div>
            </div>
          ))}
        </div>
      )}

      {list.length === 0 && (
        <div style={{ textAlign: 'center', padding: '80px 0' }}>
          <div style={{ width: '72px', height: '72px', borderRadius: '50%', background: '#1e2c3a', border: '1px solid #2b3a4a', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
            <BellOff size={32} color="#4a6278" />
          </div>
          <p style={{ color: '#e8f0f8', fontSize: '18px', fontWeight: '600', margin: '0 0 8px' }}>Нет уведомлений</p>
          <p style={{ color: '#4a6278', fontSize: '14px', margin: 0 }}>Мы сообщим о важных событиях</p>
        </div>
      )}

      {list.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {list.map((n: any, i: number) => {
            const ic = getIcon(n.type);
            const Icon = ic.Icon;
            const isUnread = !n.is_read;
            return (
              <div key={n.id} className={`tg-notif${isUnread ? ' unread' : ''}`} style={{ animation: `fadeUp 0.3s ease ${i * 40}ms both` }}>
                <div style={{ width: '44px', height: '44px', borderRadius: '12px', flexShrink: 0, background: ic.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', color: ic.color }}>
                  <Icon size={20} />
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px', flexWrap: 'wrap' }}>
                    <span style={{ color: '#e8f0f8', fontWeight: '600', fontSize: '14px' }}>{n.title || 'Уведомление'}</span>
                    {isUnread && <span style={{ padding: '2px 8px', background: 'rgba(33,150,243,0.15)', color: '#2196f3', borderRadius: '20px', fontSize: '11px', fontWeight: '600' }}>Новое</span>}
                  </div>
                  <p style={{ color: '#8ba4b8', fontSize: '13px', margin: '0 0 8px', lineHeight: 1.5 }}>{n.message || 'У вас новое уведомление'}</p>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                    <span style={{ color: '#4a6278', fontSize: '11px' }}>{formatDate(n.created_at)}</span>
                    {n.type && <span style={{ color: '#4a6278', fontSize: '11px' }}>· {typeLabel[n.type] || n.type}</span>}
                    {n.link && <a href={n.link} style={{ color: '#2196f3', fontSize: '11px', textDecoration: 'none' }}>· Перейти</a>}
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', flexShrink: 0 }}>
                  {isUnread && <button className="tg-icon-btn"><Check size={15} color="#4caf50" /></button>}
                  <button className="tg-icon-btn danger"><Trash2 size={15} color="#ef5350" /></button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {list.length >= 10 && (
        <div style={{ textAlign: 'center', marginTop: '24px' }}>
          <button style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '12px 24px', borderRadius: '10px', background: 'transparent', border: '1.5px solid #2b3a4a', color: '#8ba4b8', fontSize: '14px', fontWeight: '600', cursor: 'pointer', fontFamily: 'inherit' }}>
            <Bell size={15} /> Загрузить старые
          </button>
        </div>
      )}
    </div>
  );
};