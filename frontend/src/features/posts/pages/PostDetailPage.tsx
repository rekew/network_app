import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { postsApi } from '@/shared/api';
import { formatDate } from '@/shared/lib/utils';
import { useAuth } from '@/features/auth/context/AuthContext';
import { useState } from 'react';
import { ArrowLeft, Trash2, Clock, MessageSquare, Heart, Send, Users, Edit2, X, Check } from 'lucide-react';

const S = `
  @keyframes fadeUp { from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)} }
  @keyframes spin { to{transform:rotate(360deg)} }
  .tg-card{ background:#1e2c3a; border:1px solid #2b3a4a; border-radius:14px; }
  .tg-tag{ display:inline-flex; padding:4px 10px; border-radius:20px; font-size:12px; font-weight:500; background:rgba(33,150,243,.1); color:#2196f3; border:1px solid rgba(33,150,243,.2); cursor:pointer; transition:background .15s; }
  .tg-tag:hover{ background:rgba(33,150,243,.18); }
  .tg-btn{ display:inline-flex; align-items:center; gap:7px; padding:9px 16px; border-radius:10px; font-size:13px; font-weight:600; border:none; cursor:pointer; transition:all .2s; font-family:inherit; }
  .tg-btn-primary{ background:#2196f3; color:#fff; }
  .tg-btn-primary:hover:not(:disabled){ background:#1e88e5; }
  .tg-btn-primary:disabled{ opacity:.4; cursor:not-allowed; }
  .tg-btn-outline{ background:transparent; color:#8ba4b8; border:1.5px solid #2b3a4a; }
  .tg-btn-outline:hover{ border-color:#4a6278; color:#e8f0f8; }
  .tg-btn-danger{ background:transparent; color:#ef5350; border:1.5px solid rgba(239,83,80,.3); }
  .tg-btn-danger:hover{ background:rgba(239,83,80,.08); }
  .tg-textarea{ width:100%; background:#242f3d; border:1.5px solid #2b3a4a; border-radius:10px; padding:12px 14px; color:#e8f0f8; font-size:14px; outline:none; transition:border-color .2s; resize:none; box-sizing:border-box; font-family:inherit; }
  .tg-textarea::placeholder{ color:#4a6278; }
  .tg-textarea:focus{ border-color:#2196f3; }
  .tg-comment{ display:flex; gap:12px; padding:14px 0; border-bottom:1px solid #242f3d; animation:fadeUp .3s ease both; }
  .tg-comment:last-child{ border-bottom:none; }
  .av-stack{ display:flex; }
  .av-stack a{ width:22px; height:22px; border-radius:50%; border:2px solid #1e2c3a; margin-left:-5px; display:flex; align-items:center; justify-content:center; font-size:9px; font-weight:700; color:#fff; text-decoration:none; transition:transform .15s; }
  .av-stack a:first-child{ margin-left:0; }
  .av-stack a:hover{ transform:scale(1.15); z-index:1; }
`;

export const PostDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [comment, setComment] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState('');
  const queryClient = useQueryClient();

  const { data: post, isLoading } = useQuery({
    queryKey: ['post', id],
    queryFn: () => postsApi.get(id!),
    enabled: !!id,
  });

  const { data: comments = [] } = useQuery({
    queryKey: ['post-comments', id],
    queryFn: () => postsApi.getComments(id!),
    enabled: !!id,
  });

  const createCommentMutation = useMutation({
    mutationFn: ({ content }: { content: string }) => {
      if (!token) throw new Error('Не авторизован');
      return postsApi.createComment(id!, { content }, token);
    },
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['post-comments', id] }); setComment(''); },
  });

  const likeMutation = useMutation({
    mutationFn: () => { if (!token) throw new Error(''); return postsApi.like(id!, token); },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['post', id] }),
  });
  const unlikeMutation = useMutation({
    mutationFn: () => { if (!token) throw new Error(''); return postsApi.unlike(id!, token); },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['post', id] }),
  });
  const updatePostMutation = useMutation({
    mutationFn: (data: { content: string }) => { if (!token) throw new Error(''); return postsApi.update(id!, data); },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['post', id] });
      queryClient.invalidateQueries({ queryKey: ['posts'] });
      if (user?.id) queryClient.invalidateQueries({ queryKey: ['user-posts', user.id] });
      setIsEditing(false);
    },
    onError: (err: any) => alert(err?.response?.data?.detail || 'Не удалось обновить'),
  });

  const handleLike = () => {
    if (!user || !token || !post) return;
    post.is_liked ? unlikeMutation.mutate() : likeMutation.mutate();
  };

  if (isLoading) return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh', background: '#17212b' }}>
      <div style={{ width: '36px', height: '36px', border: '3px solid #2b3a4a', borderTop: '3px solid #2196f3', borderRadius: '50%', animation: 'spin .8s linear infinite' }} />
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
    </div>
  );

  if (!post) return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh', background: '#17212b', flexDirection: 'column', gap: '16px', fontFamily: 'inherit' }}>
      <style>{S}</style>
      <MessageSquare size={40} color="#2b3a4a" />
      <p style={{ color: '#e8f0f8', fontSize: '18px', margin: 0 }}>Пост не найден</p>
      <button className="tg-btn tg-btn-outline" onClick={() => navigate('/posts')}><ArrowLeft size={15} /> Назад</button>
    </div>
  );

  const isAuthor = post.is_author || user?.id === post.author;
  const commentsArr = Array.isArray(comments) ? comments : (comments as any)?.results || [];

  return (
    <div style={{ minHeight: '100vh', background: '#17212b', fontFamily: "'SF Pro Display',-apple-system,BlinkMacSystemFont,sans-serif", padding: '24px 20px', maxWidth: '760px', margin: '0 auto' }}>
      <style>{S}</style>

      <button className="tg-btn tg-btn-outline" onClick={() => navigate('/posts')} style={{ marginBottom: '24px' }}>
        <ArrowLeft size={15} /> Назад
      </button>

      {/* Post card */}
      <div className="tg-card" style={{ marginBottom: '16px', animation: 'fadeUp .3s ease' }}>

        {/* Header */}
        <div style={{ padding: '18px 20px', borderBottom: '1px solid #242f3d', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', flexWrap: 'wrap' }}>
          {post.community ? (
            <Link to={`/communities/${post.community}`} style={{ display: 'flex', alignItems: 'center', gap: '12px', textDecoration: 'none', flex: 1 }}>
              <div style={{ width: '44px', height: '44px', borderRadius: '12px', background: 'linear-gradient(135deg,#4caf50,#009688)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: '700', fontSize: '18px', flexShrink: 0 }}>
                {post.community_name?.[0]?.toUpperCase() || 'C'}
              </div>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ color: '#e8f0f8', fontWeight: '600', fontSize: '15px' }}>{post.community_name}</span>
                  <span style={{ padding: '2px 8px', borderRadius: '20px', fontSize: '11px', fontWeight: '600', background: 'rgba(33,150,243,.1)', color: '#2196f3', display: 'inline-flex', alignItems: 'center', gap: '3px' }}>
                    <Users size={9} /> сообщество
                  </span>
                </div>
                <div style={{ color: '#4a6278', fontSize: '12px', marginTop: '2px', display: 'flex', gap: '4px', alignItems: 'center' }}>
                  <Clock size={10} /> {formatDate(post.created_at)}
                  {post.edited_at && <span> · ред. {formatDate(post.edited_at)}</span>}
                  <span> · </span>
                  <Link to={`/profile/${post.author}`} onClick={e => e.stopPropagation()} style={{ color: '#2196f3', textDecoration: 'none' }}>от {post.author_username}</Link>
                </div>
              </div>
            </Link>
          ) : (
            <Link to={`/profile/${post.author}`} style={{ display: 'flex', alignItems: 'center', gap: '12px', textDecoration: 'none', flex: 1 }}>
              <div style={{ width: '44px', height: '44px', borderRadius: '50%', background: 'linear-gradient(135deg,#2196f3,#9c27b0)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: '700', fontSize: '18px', flexShrink: 0 }}>
                {post.author_username?.[0]?.toUpperCase() || 'U'}
              </div>
              <div>
                <div style={{ color: '#e8f0f8', fontWeight: '600', fontSize: '15px' }}>{post.author_username}</div>
                <div style={{ color: '#4a6278', fontSize: '12px', marginTop: '2px', display: 'flex', gap: '4px', alignItems: 'center' }}>
                  <Clock size={10} /> {formatDate(post.created_at)}
                  {post.edited_at && <span> · ред.</span>}
                </div>
              </div>
            </Link>
          )}

          {isAuthor && (
            <div style={{ display: 'flex', gap: '8px', flexShrink: 0 }}>
              {post.can_edit && !isEditing && (
                <button className="tg-btn tg-btn-outline" onClick={() => { setEditedContent(post.content); setIsEditing(true); }}>
                  <Edit2 size={14} /> Ред.
                </button>
              )}
              {!post.can_edit && isAuthor && (
                <span style={{ color: '#4a6278', fontSize: '12px', alignSelf: 'center' }}>Ред. недоступно</span>
              )}
              <button className="tg-btn tg-btn-danger"><Trash2 size={14} /> Удалить</button>
            </div>
          )}
        </div>

        {/* Content */}
        <div style={{ padding: '18px 20px' }}>
          {isEditing ? (
            <div style={{ marginBottom: '16px' }}>
              <textarea className="tg-textarea" value={editedContent} onChange={e => setEditedContent(e.target.value)} rows={8} placeholder="Текст поста..." />
              <div style={{ display: 'flex', gap: '8px', marginTop: '10px' }}>
                <button className="tg-btn tg-btn-primary" onClick={() => { if (editedContent.trim() && editedContent !== post.content) updatePostMutation.mutate({ content: editedContent }); else setIsEditing(false); }} disabled={updatePostMutation.isPending || !editedContent.trim()}>
                  {updatePostMutation.isPending ? 'Сохр...' : <><Check size={14} /> Сохранить</>}
                </button>
                <button className="tg-btn tg-btn-outline" onClick={() => setIsEditing(false)} disabled={updatePostMutation.isPending}>
                  <X size={14} /> Отмена
                </button>
              </div>
            </div>
          ) : (
            <p style={{ color: '#e8f0f8', fontSize: '15px', lineHeight: 1.7, margin: '0 0 16px', whiteSpace: 'pre-wrap' }}>{post.content}</p>
          )}

          {/* Tags */}
          {post.tags?.length > 0 && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '18px', paddingBottom: '18px', borderBottom: '1px solid #242f3d' }}>
              {post.tags.map((tag: any) => <span key={tag.id} className="tg-tag">#{tag.name}</span>)}
            </div>
          )}

          {/* Actions */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <button
              onClick={handleLike}
              disabled={!user || likeMutation.isPending || unlikeMutation.isPending}
              style={{ display: 'flex', alignItems: 'center', gap: '7px', fontSize: '14px', fontWeight: '500', background: post.is_liked ? 'rgba(244,67,54,.1)' : 'transparent', border: `1.5px solid ${post.is_liked ? 'rgba(244,67,54,.3)' : '#2b3a4a'}`, color: post.is_liked ? '#f44336' : '#4a6278', borderRadius: '10px', padding: '8px 14px', cursor: 'pointer', transition: 'all .15s', fontFamily: 'inherit' }}
            >
              <Heart size={16} fill={post.is_liked ? '#f44336' : 'none'} stroke={post.is_liked ? '#f44336' : '#4a6278'} />
              {post.likes_count ?? 0} {post.likes_count === 1 ? 'лайк' : 'лайков'}
            </button>
            {post.liked_by?.length > 0 && (
              <div className="av-stack">
                {post.liked_by.slice(0, 5).map((u: any) => (
                  <Link key={u.id} to={`/profile/${u.id}`} style={{ background: 'linear-gradient(135deg,#f44336,#e91e63)' }} title={u.username}>{u.username?.[0]?.toUpperCase()}</Link>
                ))}
                {post.liked_by.length > 5 && <span style={{ color: '#4a6278', fontSize: '11px', marginLeft: '7px', alignSelf: 'center' }}>+{post.liked_by.length - 5}</span>}
              </div>
            )}
            <div style={{ display: 'flex', alignItems: 'center', gap: '7px', fontSize: '14px', color: '#4a6278', marginLeft: '4px' }}>
              <MessageSquare size={16} /> {commentsArr.length} комментариев
            </div>
            {post.comment_authors?.length > 0 && (
              <div className="av-stack">
                {post.comment_authors.slice(0, 5).map((u: any) => (
                  <Link key={u.id} to={`/profile/${u.id}`} style={{ background: 'linear-gradient(135deg,#2196f3,#9c27b0)' }} title={u.username}>{u.username?.[0]?.toUpperCase()}</Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Comments */}
      <div className="tg-card" style={{ padding: '20px' }}>
        <div style={{ color: '#8ba4b8', fontSize: '11px', fontWeight: '700', letterSpacing: '.07em', textTransform: 'uppercase', marginBottom: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <MessageSquare size={13} /> Комментарии · {commentsArr.length}
        </div>

        {/* Comment form */}
        <div style={{ display: 'flex', gap: '12px', marginBottom: '20px', paddingBottom: '20px', borderBottom: '1px solid #242f3d' }}>
          <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'linear-gradient(135deg,#2196f3,#9c27b0)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: '700', fontSize: '14px', flexShrink: 0 }}>
            {user?.username?.[0]?.toUpperCase() || 'U'}
          </div>
          <div style={{ flex: 1 }}>
            <textarea
              className="tg-textarea"
              placeholder="Напишите комментарий..."
              value={comment}
              onChange={e => setComment(e.target.value)}
              rows={3}
              onKeyDown={e => { if (e.key === 'Enter' && e.ctrlKey && comment.trim()) { e.preventDefault(); createCommentMutation.mutate({ content: comment }); } }}
            />
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '8px' }}>
              <button
                className="tg-btn tg-btn-primary"
                onClick={() => { if (comment.trim()) createCommentMutation.mutate({ content: comment }); }}
                disabled={createCommentMutation.isPending || !comment.trim()}
              >
                {createCommentMutation.isPending
                  ? <><div style={{ width: '14px', height: '14px', border: '2px solid rgba(255,255,255,.3)', borderTop: '2px solid #fff', borderRadius: '50%', animation: 'spin .7s linear infinite' }} /> Отправка...</>
                  : <><Send size={14} /> Отправить</>}
              </button>
            </div>
          </div>
        </div>

        {/* Comments list */}
        {commentsArr.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '32px 0' }}>
            <MessageSquare size={32} color="#2b3a4a" style={{ marginBottom: '10px' }} />
            <p style={{ color: '#4a6278', fontSize: '14px', margin: 0 }}>Пока нет комментариев. Будьте первым!</p>
          </div>
        ) : (
          <div>
            {commentsArr.map((c: any, i: number) => (
              <div key={c.id} className="tg-comment" style={{ animationDelay: `${i * 40}ms` }}>
                <Link to={`/profile/${c.author}`} style={{ flexShrink: 0 }}>
                  <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'linear-gradient(135deg,#4caf50,#009688)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: '700', fontSize: '14px' }}>
                    {c.author_username?.[0]?.toUpperCase() || 'U'}
                  </div>
                </Link>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '5px' }}>
                    <Link to={`/profile/${c.author}`} style={{ color: '#e8f0f8', fontWeight: '600', fontSize: '13px', textDecoration: 'none' }}>{c.author_username}</Link>
                    <span style={{ color: '#4a6278', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '3px' }}><Clock size={9} /> {formatDate(c.created_at)}</span>
                  </div>
                  <p style={{ color: '#8ba4b8', fontSize: '14px', margin: 0, lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>{c.content}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};