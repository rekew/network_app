import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { communitiesApi } from '@/shared/api';
import { Users, Plus, Globe, Lock, Eye, Search, X } from 'lucide-react';

const S = `
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .tg-card {
    background: #1e2c3a;
    border: 1px solid #2b3a4a;
    border-radius: 14px;
    transition: border-color 0.2s, transform 0.2s;
    cursor: pointer;
    text-decoration: none;
    display: block;
    color: inherit;
  }
  .tg-card:hover { border-color: #2196f3; transform: translateY(-2px); }
  .tg-input {
    background: #242f3d;
    border: 1.5px solid #2b3a4a;
    border-radius: 10px;
    padding: 11px 16px 11px 40px;
    color: #e8f0f8;
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s;
    width: 100%;
    box-sizing: border-box;
    font-family: inherit;
  }
  .tg-input::placeholder { color: #4a6278; }
  .tg-input:focus { border-color: #2196f3; }
  .tg-chip {
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    border: 1px solid;
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }
`;

const visibilityConfig: Record<string, { label: string; color: string; bg: string }> = {
  public:  { label: 'Публичное',  color: '#4caf50', bg: 'rgba(76,175,80,0.1)' },
  private: { label: 'Приватное', color: '#ff9800', bg: 'rgba(255,152,0,0.1)' },
  secret:  { label: 'Секретное', color: '#f44336', bg: 'rgba(244,67,54,0.1)' },
};

const VisibilityIcon = ({ v }: { v: string }) => {
  if (v === 'public') return <Globe size={13} />;
  if (v === 'private') return <Lock size={13} />;
  return <Eye size={13} />;
};

export const CommunitiesListPage = () => {
  const [searchInput, setSearchInput] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filter, setFilter] = useState('');

  useEffect(() => {
    const t = setTimeout(() => setSearchQuery(searchInput.trim()), 400);
    return () => clearTimeout(t);
  }, [searchInput]);

  const { data: communities, isLoading } = useQuery({
    queryKey: ['communities', searchQuery, filter],
    queryFn: () => communitiesApi.list({
      ...(searchQuery && { search: searchQuery }),
      ...(filter && { visibility: filter }),
    }),
  });

  const list = Array.isArray(communities) ? communities : (communities as any)?.results || [];

  return (
    <div style={{
      minHeight: '100vh',
      background: '#17212b',
      fontFamily: "'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif",
      padding: '24px 20px',
      maxWidth: '900px',
      margin: '0 auto',
    }}>
      <style>{S}</style>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '28px' }}>
        <div>
          <h1 style={{ color: '#e8f0f8', fontSize: '26px', fontWeight: '700', margin: '0 0 4px' }}>Сообщества</h1>
          <p style={{ color: '#4a6278', fontSize: '14px', margin: 0 }}>
            {list.length > 0 ? `${list.length} сообществ` : 'Пока нет сообществ'}
          </p>
        </div>
        <Link to="/communities/create" style={{
          display: 'inline-flex', alignItems: 'center', gap: '8px',
          background: '#2196f3', color: '#fff', textDecoration: 'none',
          padding: '10px 18px', borderRadius: '10px', fontSize: '14px', fontWeight: '600',
          transition: 'background 0.2s',
        }}>
          <Plus size={16} /> Создать
        </Link>
      </div>

      {/* Search + Filter */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '24px', flexWrap: 'wrap' }}>
        <div style={{ position: 'relative', flex: 1, minWidth: '200px' }}>
          <Search size={16} style={{ position: 'absolute', left: '13px', top: '50%', transform: 'translateY(-50%)', color: '#4a6278' }} />
          <input
            className="tg-input"
            placeholder="Поиск сообществ..."
            value={searchInput}
            onChange={e => setSearchInput(e.target.value)}
          />
          {searchInput && (
            <button onClick={() => { setSearchInput(''); setSearchQuery(''); }} style={{
              position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)',
              background: 'none', border: 'none', color: '#4a6278', cursor: 'pointer', padding: 0,
            }}>
              <X size={14} />
            </button>
          )}
        </div>
        {['', 'public', 'private', 'secret'].map(v => (
          <button key={v} onClick={() => setFilter(v)} style={{
            padding: '10px 16px', borderRadius: '10px', fontSize: '13px', fontWeight: '600',
            border: '1.5px solid', cursor: 'pointer', transition: 'all 0.2s',
            fontFamily: 'inherit',
            background: filter === v ? '#2196f3' : '#1e2c3a',
            borderColor: filter === v ? '#2196f3' : '#2b3a4a',
            color: filter === v ? '#fff' : '#8ba4b8',
          }}>
            {v === '' ? 'Все' : v === 'public' ? 'Публичные' : v === 'private' ? 'Приватные' : 'Секретные'}
          </button>
        ))}
      </div>

      {/* Loading */}
      {isLoading && (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '60px 0' }}>
          <div style={{
            width: '36px', height: '36px',
            border: '3px solid #2b3a4a', borderTop: '3px solid #2196f3',
            borderRadius: '50%', animation: 'spin 0.8s linear infinite',
          }} />
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </div>
      )}

      {/* Empty */}
      {!isLoading && list.length === 0 && (
        <div style={{ textAlign: 'center', padding: '80px 0' }}>
          <div style={{
            width: '72px', height: '72px', borderRadius: '50%',
            background: '#1e2c3a', border: '1px solid #2b3a4a',
            display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
            marginBottom: '16px',
          }}>
            <Users size={32} color="#4a6278" />
          </div>
          <p style={{ color: '#e8f0f8', fontSize: '18px', fontWeight: '600', margin: '0 0 8px' }}>Нет сообществ</p>
          <p style={{ color: '#4a6278', fontSize: '14px', margin: '0 0 24px' }}>Создайте первое сообщество!</p>
          <Link to="/communities/create" style={{
            background: '#2196f3', color: '#fff', textDecoration: 'none',
            padding: '12px 24px', borderRadius: '10px', fontSize: '14px', fontWeight: '600',
          }}>
            Создать сообщество
          </Link>
        </div>
      )}

      {/* Grid */}
      {!isLoading && list.length > 0 && (
        <div style={{ display: 'grid', gap: '12px', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))' }}>
          {list.map((c: any, i: number) => {
            const vis = visibilityConfig[c.visibility] || visibilityConfig.public;
            return (
              <Link
                key={c.id}
                to={`/communities/${c.id}`}
                className="tg-card"
                style={{ padding: '20px', animation: `fadeUp 0.3s ease ${i * 40}ms both` }}
              >
                {/* Avatar */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '14px' }}>
                  <div style={{
                    width: '48px', height: '48px', borderRadius: '14px', flexShrink: 0,
                    background: 'linear-gradient(135deg, #2196f3, #1565c0)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    <Users size={22} color="#fff" />
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ color: '#e8f0f8', fontWeight: '600', fontSize: '15px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {c.name}
                    </div>
                    <div style={{ color: '#4a6278', fontSize: '12px', marginTop: '2px' }}>
                      {c.members_count || 0} участников
                    </div>
                  </div>
                </div>

                {/* Description */}
                {c.description && (
                  <p style={{ color: '#8ba4b8', fontSize: '13px', margin: '0 0 14px', lineHeight: 1.5, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    {c.description}
                  </p>
                )}

                {/* Badge */}
                <span className="tg-chip" style={{ color: vis.color, borderColor: vis.color, background: vis.bg }}>
                  <VisibilityIcon v={c.visibility} />
                  {vis.label}
                </span>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
};