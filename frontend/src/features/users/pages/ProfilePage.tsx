import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/features/auth/context/AuthContext';
import { usersApi, postsApi } from '@/shared/api';
import { formatDate } from '@/shared/lib/utils';
import type { Post, Profile } from '@/shared/types';
import { Edit2, Camera, MapPin, Calendar, Mail, Phone, Globe, Clock, MessageSquare, Heart, X } from 'lucide-react';

const S = `
  @keyframes fadeUp { from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)} }
  @keyframes spin { to{transform:rotate(360deg)} }
  .tg-card{ background:#1e2c3a; border:1px solid #2b3a4a; border-radius:14px; }
  .tg-input,.tg-textarea,.tg-select{
    width:100%; background:#242f3d; border:1.5px solid #2b3a4a; border-radius:10px;
    padding:11px 14px; color:#e8f0f8; font-size:14px; outline:none;
    transition:border-color .2s; box-sizing:border-box; font-family:inherit;
  }
  .tg-input::placeholder,.tg-textarea::placeholder{ color:#4a6278; }
  .tg-input:focus,.tg-textarea:focus,.tg-select:focus{ border-color:#2196f3; }
  .tg-textarea{ resize:none; }
  .tg-select option{ background:#242f3d; }
  .tg-btn{ display:inline-flex; align-items:center; gap:7px; padding:10px 16px; border-radius:10px; font-size:14px; font-weight:600; cursor:pointer; border:none; transition:all .2s; font-family:inherit; }
  .tg-btn-primary{ background:#2196f3; color:#fff; }
  .tg-btn-primary:hover:not(:disabled){ background:#1e88e5; }
  .tg-btn-primary:disabled{ opacity:.4; cursor:not-allowed; }
  .tg-btn-outline{ background:transparent; color:#8ba4b8; border:1.5px solid #2b3a4a; }
  .tg-btn-outline:hover{ border-color:#4a6278; color:#e8f0f8; }
  .tg-label{ color:#8ba4b8; font-size:11px; font-weight:700; letter-spacing:.07em; text-transform:uppercase; display:block; margin-bottom:7px; }
  .tg-field{ margin-bottom:16px; }
  .tg-tag{ display:inline-flex; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:500; background:rgba(33,150,243,.1); color:#2196f3; border:1px solid rgba(33,150,243,.2); }
  .tg-post-card{ background:#17212b; border:1px solid #242f3d; border-radius:12px; overflow:hidden; transition:border-color .2s; }
  .tg-post-card:hover{ border-color:#2b3a4a; }
  @media(max-width:700px){ .profile-grid{ grid-template-columns:1fr !important; } }
`;

const normalizeInterests = (interests: any): string[] => {
  if (!interests) return [];
  if (Array.isArray(interests)) return interests.map(String);
  if (typeof interests === 'object') return Object.values(interests).map(String);
  return [String(interests)];
};

export const ProfilePage = () => {
  const { userId } = useParams<{ userId?: string }>();
  const { user: currentUser, isLoading: authLoading, refreshUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);
  const [formData, setFormData] = useState({ display_name: '', bio: '', location: '', interests: [] as string[], gender: 'other' as 'male' | 'female' | 'other', avatar: null as File | null });
  const [interestsInput, setInterestsInput] = useState('');

  const { data: profileData, isLoading: profileLoading, error: profileError, refetch: refetchProfile } = useQuery({
    queryKey: ['profile', userId || 'me'],
    queryFn: async () => {
      if (!userId) {
        if (!currentUser) throw new Error('Не авторизован');
        const profile = await usersApi.getProfile(currentUser.id); 
        return { profile: { ...profile, interests: normalizeInterests(profile.interests) }, user: currentUser };
      }
      
      const [user, profile] = await Promise.all([
        usersApi.get(userId),           
        usersApi.getProfile(userId),    
      ]);
      return { profile: { ...profile, interests: normalizeInterests(profile.interests) }, user };
    },
    enabled: !userId ? (!authLoading && !!currentUser) : !authLoading,
    retry: 1, staleTime: 30000,
  });

  const profile = profileData?.profile;
  const user = profileData?.user || currentUser;
  const isOwnProfile = !userId || (currentUser && userId === currentUser.id);
  const targetUserId = userId || user?.id || currentUser?.id;

  const { data: userPosts = [], isLoading: postsLoading, refetch: refetchPosts } = useQuery({
    queryKey: ['user-posts', targetUserId],
    queryFn: () => { if (!targetUserId) throw new Error(''); return postsApi.getUserPosts(targetUserId); },
    enabled: !!targetUserId, retry: 1,
  });

  useEffect(() => { if (targetUserId) refetchPosts(); }, [targetUserId, refetchPosts]);

  useEffect(() => {
    if (profile) {
      const arr = normalizeInterests(profile.interests);
      setFormData({ display_name: profile.display_name || '', bio: profile.bio || '', location: profile.location || '', interests: arr, gender: profile.gender || 'other', avatar: null });
      setInterestsInput(arr.join(', '));
      if (profile.avatar) setAvatarPreview(profile.avatar);
    }
  }, [profile]);

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFormData(p => ({ ...p, avatar: file }));
      const reader = new FileReader();
      reader.onloadend = () => setAvatarPreview(reader.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleSave = async () => {
  if (!currentUser || !isOwnProfile) return;
  try {
    setIsSaving(true);
    const fd = new FormData();
    if (formData.avatar) fd.append('avatar', formData.avatar);
    fd.append('display_name', formData.display_name);
    fd.append('bio', formData.bio);
    fd.append('location', formData.location);
    fd.append('gender', formData.gender);
    formData.interests.forEach(i => fd.append('interests', i));

    await usersApi.updateProfile(currentUser.id, fd);  
    setIsEditing(false);
    await refetchProfile();
    await refreshUser();
  } catch (err: any) {
    alert(err?.response?.data?.detail || err?.message || 'Не удалось обновить профиль');
  } finally { setIsSaving(false); }
};

  const handleCancel = () => {
    if (profile) {
      const arr = normalizeInterests(profile.interests);
      setFormData({ display_name: profile.display_name || '', bio: profile.bio || '', location: profile.location || '', interests: arr, gender: profile.gender || 'other', avatar: null });
      setInterestsInput(arr.join(', '));
      setAvatarPreview(profile.avatar || null);
    }
    setIsEditing(false);
  };

  // Loading
  if (authLoading || profileLoading) return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh', background: '#17212b', flexDirection: 'column', gap: '12px' }}>
      <div style={{ width: '36px', height: '36px', border: '3px solid #2b3a4a', borderTop: '3px solid #2196f3', borderRadius: '50%', animation: 'spin .8s linear infinite' }} />
      <p style={{ color: '#4a6278', fontSize: '14px', margin: 0 }}>{authLoading ? 'Загрузка пользователя...' : 'Загрузка профиля...'}</p>
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
    </div>
  );

  // Error
  if (profileError || !user || !profile) return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh', background: '#17212b', flexDirection: 'column', gap: '16px', fontFamily: 'inherit' }}>
      <style>{S}</style>
      <p style={{ color: '#e8f0f8', fontSize: '18px', margin: 0 }}>
        {profileError ? 'Ошибка загрузки профиля' : 'Пользователь не найден'}
      </p>
      {profileError && <p style={{ color: '#4a6278', fontSize: '14px', margin: 0 }}>{profileError instanceof Error ? profileError.message : 'Неизвестная ошибка'}</p>}
      <button className="tg-btn tg-btn-primary" onClick={() => refetchProfile()}>Попробовать снова</button>
    </div>
  );

  const displayName = profile.display_name || user.username || user.email;
  const postsArr = Array.isArray(userPosts) ? userPosts : (userPosts as any)?.results || [];

  return (
    <div style={{ minHeight: '100vh', background: '#17212b', fontFamily: "'SF Pro Display',-apple-system,BlinkMacSystemFont,sans-serif", padding: '24px 20px', maxWidth: '960px', margin: '0 auto' }}>
      <style>{S}</style>

      {/* Profile header card */}
      <div className="tg-card" style={{ padding: '28px', marginBottom: '20px', animation: 'fadeUp .3s ease' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '24px', flexWrap: 'wrap' }}>

          {/* Avatar */}
          <div style={{ position: 'relative', flexShrink: 0 }}>
            {avatarPreview ? (
              <img src={avatarPreview} alt="avatar" style={{ width: '88px', height: '88px', borderRadius: '50%', objectFit: 'cover', border: '3px solid #2b3a4a' }} />
            ) : (
              <div style={{ width: '88px', height: '88px', borderRadius: '50%', background: 'linear-gradient(135deg,#2196f3,#9c27b0)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: '700', fontSize: '34px', border: '3px solid #2b3a4a' }}>
                {displayName[0]?.toUpperCase()}
              </div>
            )}
            {isEditing && (
              <label style={{ position: 'absolute', bottom: '0', right: '0', background: '#2196f3', borderRadius: '50%', padding: '7px', cursor: 'pointer', display: 'flex', border: '2px solid #17212b' }}>
                <Camera size={14} color="#fff" />
                <input type="file" accept="image/*" onChange={handleAvatarChange} style={{ display: 'none' }} />
              </label>
            )}
          </div>

          {/* Info */}
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '12px', flexWrap: 'wrap' }}>
              <div>
                <h1 style={{ color: '#e8f0f8', fontSize: '22px', fontWeight: '700', margin: '0 0 4px' }}>{displayName}</h1>
                {user.username && <p style={{ color: '#4a6278', fontSize: '14px', margin: '0 0 8px' }}>@{user.username}</p>}
                {profile.is_verified && (
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '3px 10px', borderRadius: '20px', fontSize: '12px', fontWeight: '600', background: 'rgba(33,150,243,.1)', color: '#2196f3', border: '1px solid rgba(33,150,243,.2)' }}>
                    ✓ Верифицирован
                  </span>
                )}
              </div>
              {isOwnProfile && !isEditing && (
                <button className="tg-btn tg-btn-outline" onClick={() => setIsEditing(true)}>
                  <Edit2 size={14} /> Редактировать
                </button>
              )}
            </div>

            {profile.bio && !isEditing && (
              <p style={{ color: '#8ba4b8', fontSize: '14px', margin: '10px 0', lineHeight: 1.6 }}>{profile.bio}</p>
            )}

            {/* Meta */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', marginTop: '12px' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ color: '#e8f0f8', fontSize: '22px', fontWeight: '700' }}>{postsArr.length}</div>
                <div style={{ color: '#4a6278', fontSize: '12px' }}>постов</div>
              </div>
              {profile.location && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#8ba4b8', fontSize: '13px' }}>
                  <MapPin size={14} color="#4a6278" /> {profile.location}
                </div>
              )}
              {user.date_joined && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#8ba4b8', fontSize: '13px' }}>
                  <Calendar size={14} color="#4a6278" /> с {new Date(user.date_joined).toLocaleDateString('ru-RU', { month: 'long', year: 'numeric' })}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Two-column layout */}
      <div className="profile-grid" style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '16px', alignItems: 'start' }}>

        {/* Left: About + Edit form */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div className="tg-card" style={{ padding: '20px' }}>
            <div style={{ color: '#8ba4b8', fontSize: '11px', fontWeight: '700', letterSpacing: '.07em', textTransform: 'uppercase', marginBottom: '16px' }}>О пользователе</div>

            {isEditing ? (
              <>
                <div className="tg-field">
                  <label className="tg-label">Имя</label>
                  <input className="tg-input" value={formData.display_name} onChange={e => setFormData(p => ({ ...p, display_name: e.target.value }))} placeholder="Отображаемое имя" />
                </div>
                <div className="tg-field">
                  <label className="tg-label">О себе</label>
                  <textarea className="tg-textarea" value={formData.bio} onChange={e => setFormData(p => ({ ...p, bio: e.target.value }))} placeholder="Расскажите о себе..." rows={4} />
                </div>
                <div className="tg-field">
                  <label className="tg-label">Местоположение</label>
                  <input className="tg-input" value={formData.location} onChange={e => setFormData(p => ({ ...p, location: e.target.value }))} placeholder="Город, Страна" />
                </div>
                <div className="tg-field">
                  <label className="tg-label">Пол</label>
                  <select className="tg-select" value={formData.gender} onChange={e => setFormData(p => ({ ...p, gender: e.target.value as any }))}>
                    <option value="male">Мужской</option>
                    <option value="female">Женский</option>
                    <option value="other">Другой</option>
                  </select>
                </div>
                <div className="tg-field">
                  <label className="tg-label">Интересы (через запятую)</label>
                  <input className="tg-input" value={interestsInput} onChange={e => { setInterestsInput(e.target.value); setFormData(p => ({ ...p, interests: e.target.value.split(',').map(i => i.trim()).filter(Boolean) })); }} placeholder="Программирование, Музыка..." />
                </div>
                <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
                  <button className="tg-btn tg-btn-primary" onClick={handleSave} disabled={isSaving} style={{ flex: 1, justifyContent: 'center' }}>
                    {isSaving ? 'Сохр...' : 'Сохранить'}
                  </button>
                  <button className="tg-btn tg-btn-outline" onClick={handleCancel} style={{ flexShrink: 0 }}><X size={14} /></button>
                </div>
              </>
            ) : (
              <>
                {profile.bio && (
                  <div style={{ marginBottom: '14px' }}>
                    <div style={{ color: '#4a6278', fontSize: '11px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '.06em', marginBottom: '5px' }}>О себе</div>
                    <p style={{ color: '#8ba4b8', fontSize: '14px', margin: 0, lineHeight: 1.6 }}>{profile.bio}</p>
                  </div>
                )}
                {[
                  user.email && { icon: Mail, text: user.email },
                  user.phone_number && { icon: Phone, text: user.phone_number },
                  (user.city && user.country) && { icon: Globe, text: `${user.city}, ${user.country}` },
                ].filter(Boolean).map((item: any, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: '#8ba4b8', fontSize: '13px' }}>
                    <item.icon size={14} color="#4a6278" /> {item.text}
                  </div>
                ))}
                {normalizeInterests(profile.interests).length > 0 && (
                  <div style={{ marginTop: '12px' }}>
                    <div style={{ color: '#4a6278', fontSize: '11px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '.06em', marginBottom: '8px' }}>Интересы</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {normalizeInterests(profile.interests).map((interest, i) => (
                        <span key={i} className="tg-tag">{interest}</span>
                      ))}
                    </div>
                  </div>
                )}
                {!profile.bio && !user.email && !user.phone_number && normalizeInterests(profile.interests).length === 0 && (
                  <p style={{ color: '#4a6278', fontSize: '13px', margin: 0 }}>Информация не заполнена</p>
                )}
              </>
            )}
          </div>

          {/* Personal info */}
          {(user.full_name || user.first_name || user.last_name || user.birthdate || user.date_joined) && (
            <div className="tg-card" style={{ padding: '20px' }}>
              <div style={{ color: '#8ba4b8', fontSize: '11px', fontWeight: '700', letterSpacing: '.07em', textTransform: 'uppercase', marginBottom: '14px' }}>Личная информация</div>
              {[
                user.full_name && ['Полное имя', user.full_name],
                user.first_name && ['Имя', user.first_name],
                user.last_name && ['Фамилия', user.last_name],
                user.birthdate && ['Дата рождения', new Date(user.birthdate).toLocaleDateString('ru-RU')],
                user.date_joined && ['Дата регистрации', new Date(user.date_joined).toLocaleDateString('ru-RU')],
              ].filter(Boolean).map(([label, value]: any, i) => (
                <div key={i} style={{ marginBottom: '10px' }}>
                  <div style={{ color: '#4a6278', fontSize: '11px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '.06em', marginBottom: '3px' }}>{label}</div>
                  <div style={{ color: '#e8f0f8', fontSize: '13px' }}>{value}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right: Posts */}
        <div className="tg-card" style={{ padding: '20px' }}>
          <div style={{ color: '#8ba4b8', fontSize: '11px', fontWeight: '700', letterSpacing: '.07em', textTransform: 'uppercase', marginBottom: '16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span>Посты · {postsArr.length}</span>
            {isOwnProfile && <Link to="/posts/create" style={{ color: '#2196f3', fontSize: '12px', textDecoration: 'none', fontWeight: '700' }}>+ Создать</Link>}
          </div>

          {postsLoading && (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '40px 0' }}>
              <div style={{ width: '28px', height: '28px', border: '3px solid #2b3a4a', borderTop: '3px solid #2196f3', borderRadius: '50%', animation: 'spin .8s linear infinite' }} />
            </div>
          )}

          {!postsLoading && postsArr.length === 0 && (
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <MessageSquare size={36} color="#2b3a4a" style={{ marginBottom: '12px' }} />
              <p style={{ color: '#4a6278', fontSize: '14px', margin: 0 }}>
                {isOwnProfile ? 'У вас пока нет постов. Создайте первый!' : 'Нет постов'}
              </p>
            </div>
          )}

          {!postsLoading && postsArr.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {postsArr.map((post: Post, i: number) => (
                <div key={post.id} className="tg-post-card" style={{ animation: `fadeUp .3s ease ${i * 50}ms both` }}>
                  <div style={{ padding: '14px 16px', borderBottom: '1px solid #242f3d', display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{ width: '34px', height: '34px', borderRadius: '50%', background: 'linear-gradient(135deg,#2196f3,#9c27b0)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: '700', fontSize: '13px', flexShrink: 0 }}>
                      {post.author_username?.[0]?.toUpperCase() || 'U'}
                    </div>
                    <div>
                      <div style={{ color: '#e8f0f8', fontWeight: '600', fontSize: '13px' }}>{post.author_username}</div>
                      <div style={{ color: '#4a6278', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '3px' }}><Clock size={9} /> {formatDate(post.created_at)}</div>
                    </div>
                  </div>
                  <div style={{ padding: '12px 16px' }}>
                    <p style={{ color: '#8ba4b8', fontSize: '13px', margin: '0 0 12px', lineHeight: 1.6, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden', whiteSpace: 'pre-wrap' }}>
                      {post.content}
                    </p>
                    {post.tags?.length > 0 && (
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px', marginBottom: '12px' }}>
                        {post.tags.map((tag) => (
                          <span key={tag.id} style={{ padding: '2px 8px', borderRadius: '20px', fontSize: '11px', background: 'rgba(33,150,243,.1)', color: '#2196f3' }}>#{tag.name}</span>
                        ))}
                      </div>
                    )}
                    <Link to={`/posts/${post.id}`} style={{ color: '#2196f3', fontSize: '13px', fontWeight: '600', textDecoration: 'none' }}>
                      Читать далее →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};