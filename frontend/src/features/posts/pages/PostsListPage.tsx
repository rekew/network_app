import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, useSearchParams } from 'react-router-dom';
import { postsApi, communitiesApi } from '@/shared/api';
import { formatDate } from '@/shared/lib/utils';
import { useAuth } from '@/features/auth/context/AuthContext';
import { Plus, Clock, MessageSquare, Heart, Users } from 'lucide-react';

const S = `
  @keyframes fadeUp { from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)} }
  @keyframes spin { to{transform:rotate(360deg)} }
  .tg-post{ background:#1e2c3a; border:1px solid #2b3a4a; border-radius:14px; overflow:hidden; transition:border-color .2s; }
  .tg-post:hover{ border-color:#344a5e; }
  .tg-tag{ display:inline-flex; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:500; background:rgba(33,150,243,.1); color:#2196f3; border:1px solid rgba(33,150,243,.2); }
  .tg-like-btn{ display:flex; align-items:center; gap:6px; font-size:13px; font-weight:500; background:none; border:none; cursor:pointer; transition:all .15s; font-family:inherit; padding:6px 10px; border-radius:8px; }
  .tg-like-btn:hover{ background:rgba(244,67,54,.08); }
  .tg-like-btn:disabled{ opacity:.4; cursor:not-allowed; }
  .av-stack{ display:flex; }
  .av-stack a{ width:22px; height:22px; border-radius:50%; border:2px solid #1e2c3a; margin-left:-5px; display:flex; align-items:center; justify-content:center; font-size:9px; font-weight:700; color:#fff; text-decoration:none; transition:transform .15s; }
  .av-stack a:first-child{ margin-left:0; }
  .av-stack a:hover{ transform:scale(1.15); z-index:1; }
`;

export const PostsListPage = () => {
  const { user, token } = useAuth();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const communityId = searchParams.get('community');

  const { data: posts, isLoading } = useQuery({
    queryKey: ['posts', communityId],
    queryFn: () => postsApi.list(communityId ? { community: communityId } : undefined),
  });

  const { data: communityData } = useQuery({
    queryKey: ['community', communityId],
    queryFn: () => communitiesApi.get(communityId!),
    enabled: !!communityId,
  });

  const postsArray = Array.isArray(posts) ? posts : (posts as any)?.results || [];

  const likeMutation = useMutation({
    mutationFn: (postId: string) => { if (!token) throw new Error(''); return postsApi.like(postId, token); },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['posts'] }),
  });
  const unlikeMutation = useMutation({
    mutationFn: (postId: string) => { if (!token) throw new Error(''); return postsApi.unlike(postId, token); },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['posts'] }),
  });

  const handleLike = (post: any, e: React.MouseEvent) => {
    e.preventDefault(); e.stopPropagation();
    if (!user || !token) return;
    post.is_liked ? unlikeMutation.mutate(post.id) : likeMutation.mutate(post.id);
  };

  return (
    <div style={{ minHeight: '100vh', background: '#17212b', fontFamily: "'SF Pro Display',-apple-system,BlinkMacSystemFont,sans-serif", padding: '24px 20px', maxWidth: '760px', margin: '0 auto' }}>
      <style>{S}</style>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '28px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ color: '#e8f0f8', fontSize: '26px', fontWeight: '700', margin: '0 0 4px' }}>
            {communityData ? communityData.name : 'Посты'}
          </h1>
          <p style={{ color: '#4a6278', fontSize: '14px', margin: 0 }}>
            {postsArray.length > 0 ? `${postsArray.length} публикаций` : 'Пока нет постов'}
          </p>
        </div>
        <Link to="/posts/create" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: '#2196f3', color: '#fff', textDecoration: 'none', padding: '10px 18px', borderRadius: '10px', fontSize: '14px', fontWeight: '600' }}>
          <Plus size={16} /> Создать пост
        </Link>
      </div>

      {/* Loading */}
      {isLoading && (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '60px 0' }}>
          <div style={{ width: '36px', height: '36px', border: '3px solid #2b3a4a', borderTop: '3px solid #2196f3', borderRadius: '50%', animation: 'spin .8s linear infinite' }} />
        </div>
      )}

      {/* Empty */}
      {!isLoading && postsArray.length === 0 && (
        <div style={{ textAlign: 'center', padding: '80px 0' }}>
          <MessageSquare size={48} color="#2b3a4a" style={{ marginBottom: '16px' }} />
          <p style={{ color: '#e8f0f8', fontSize: '18px', fontWeight: '600', margin: '0 0 8px' }}>Нет постов</p>
          <p style={{ color: '#4a6278', fontSize: '14px', margin: '0 0 24px' }}>Станьте первым!</p>
          <Link to="/posts/create" style={{ background: '#2196f3', color: '#fff', textDecoration: 'none', padding: '12px 24px', borderRadius: '10px', fontSize: '14px', fontWeight: '600' }}>
            Создать пост
          </Link>
        </div>
      )}

      {/* Posts */}
      {!isLoading && postsArray.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {postsArray.map((post: any, i: number) => (
            <div key={post.id} className="tg-post" style={{ animation: `fadeUp .3s ease ${i * 50}ms both` }}>

              {/* Author row */}
              <div style={{ padding: '16px 18px 12px', borderBottom: '1px solid #242f3d' }}>
                {post.community ? (
                  <Link to={`/communities/${post.community}`} style={{ display: 'flex', alignItems: 'center', gap: '12px', textDecoration: 'none' }}>
                    <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'linear-gradient(135deg,#4caf50,#009688)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: '700', fontSize: '16px', flexShrink: 0 }}>
                      {post.community_name?.[0]?.toUpperCase() || 'C'}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ color: '#e8f0f8', fontWeight: '600', fontSize: '14px' }}>{post.community_name}</span>
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '3px', padding: '2px 8px', borderRadius: '20px', fontSize: '11px', fontWeight: '600', background: 'rgba(33,150,243,.1)', color: '#2196f3' }}>
                          <Users size={9} /> сообщество
                        </span>
                      </div>
                      <div style={{ color: '#4a6278', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px', marginTop: '2px' }}>
                        <Clock size={10} /> {formatDate(post.created_at)} · от {post.author_username}
                      </div>
                    </div>
                  </Link>
                ) : (
                  <Link to={`/profile/${post.author}`} style={{ display: 'flex', alignItems: 'center', gap: '12px', textDecoration: 'none' }}>
                    <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'linear-gradient(135deg,#2196f3,#9c27b0)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: '700', fontSize: '16px', flexShrink: 0 }}>
                      {post.author_username?.[0]?.toUpperCase() || 'U'}
                    </div>
                    <div>
                      <div style={{ color: '#e8f0f8', fontWeight: '600', fontSize: '14px' }}>{post.author_username}</div>
                      <div style={{ color: '#4a6278', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px', marginTop: '2px' }}>
                        <Clock size={10} /> {formatDate(post.created_at)}{post.edited_at && ' · ред.'}
                      </div>
                    </div>
                  </Link>
                )}
              </div>

              {/* Content */}
              <div style={{ padding: '14px 18px' }}>
                <p style={{ color: '#e8f0f8', fontSize: '14px', lineHeight: 1.65, margin: '0 0 10px', display: '-webkit-box', WebkitLineClamp: 4, WebkitBoxOrient: 'vertical', overflow: 'hidden', whiteSpace: 'pre-wrap' }}>
                  {post.content}
                </p>
                {post.content?.length > 200 && (
                  <Link to={`/posts/${post.id}`} style={{ color: '#2196f3', fontSize: '13px', textDecoration: 'none', fontWeight: '500' }}>Читать полностью</Link>
                )}
                {post.tags?.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '12px' }}>
                    {post.tags.map((tag: any) => <span key={tag.id} className="tg-tag">#{tag.name}</span>)}
                  </div>
                )}
              </div>

              {/* Footer */}
              <div style={{ padding: '10px 14px 14px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid #242f3d' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '2px' }}>
                  <button className="tg-like-btn" onClick={e => handleLike(post, e)} disabled={!user} style={{ color: post.is_liked ? '#f44336' : '#4a6278' }}>
                    <Heart size={15} fill={post.is_liked ? '#f44336' : 'none'} stroke={post.is_liked ? '#f44336' : '#4a6278'} /> {post.likes_count ?? 0}
                  </button>
                  {post.liked_by?.length > 0 && (
                    <div className="av-stack" style={{ marginLeft: '2px' }}>
                      {post.liked_by.slice(0, 3).map((u: any) => (
                        <Link key={u.id} to={`/profile/${u.id}`} style={{ background: 'linear-gradient(135deg,#f44336,#e91e63)' }} title={u.username}>{u.username?.[0]?.toUpperCase()}</Link>
                      ))}
                      {post.liked_by.length > 3 && <span style={{ color: '#4a6278', fontSize: '11px', marginLeft: '6px' }}>+{post.liked_by.length - 3}</span>}
                    </div>
                  )}
                  <Link to={`/posts/${post.id}`} style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#4a6278', fontSize: '13px', fontWeight: '500', textDecoration: 'none', padding: '6px 10px', borderRadius: '8px', marginLeft: '4px' }}>
                    <MessageSquare size={15} /> {post.comments_count ?? 0}
                  </Link>
                  {post.comment_authors?.length > 0 && (
                    <div className="av-stack" style={{ marginLeft: '2px' }}>
                      {post.comment_authors.slice(0, 3).map((u: any) => (
                        <Link key={u.id} to={`/profile/${u.id}`} style={{ background: 'linear-gradient(135deg,#2196f3,#9c27b0)' }} title={u.username}>{u.username?.[0]?.toUpperCase()}</Link>
                      ))}
                    </div>
                  )}
                </div>
                <Link to={`/posts/${post.id}`} style={{ color: '#2196f3', fontSize: '13px', fontWeight: '600', textDecoration: 'none', padding: '6px 14px', borderRadius: '8px', background: 'rgba(33,150,243,.08)' }}>
                  Открыть
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};