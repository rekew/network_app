import { useNavigate, useSearchParams } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { postsApi, communitiesApi } from '@/shared/api';
import { useAuth } from '@/features/auth/context/AuthContext';
import { ArrowLeft, Send, X, FileText, AlertCircle, Users, Hash, Plus } from 'lucide-react';
import { useState, useEffect } from 'react';

const postSchema = z.object({
  content: z.string().min(10, 'Минимум 10 символов'),
  community: z.string().optional(),
  tags: z.array(z.string()).optional(),
});
type PostFormData = z.infer<typeof postSchema>;

const S = `
  @keyframes fadeUp { from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)} }
  @keyframes spin { to{transform:rotate(360deg)} }
  .tg-input,.tg-textarea,.tg-select{
    width:100%; background:#242f3d; border:1.5px solid #2b3a4a; border-radius:10px;
    padding:12px 16px; color:#e8f0f8; font-size:15px; outline:none;
    transition:border-color .2s; box-sizing:border-box; font-family:inherit;
  }
  .tg-input::placeholder,.tg-textarea::placeholder{ color:#4a6278; }
  .tg-input:focus,.tg-textarea:focus,.tg-select:focus{ border-color:#2196f3; }
  .tg-input.err,.tg-textarea.err{ border-color:#f44336; }
  .tg-textarea{ resize:none; }
  .tg-select option{ background:#242f3d; }
  .tg-btn{ display:inline-flex; align-items:center; gap:8px; padding:12px 20px; border-radius:10px; font-size:15px; font-weight:600; cursor:pointer; border:none; transition:all .2s; font-family:inherit; }
  .tg-btn-primary{ background:#2196f3; color:#fff; }
  .tg-btn-primary:hover:not(:disabled){ background:#1e88e5; }
  .tg-btn-primary:disabled{ opacity:.4; cursor:not-allowed; }
  .tg-btn-outline{ background:transparent; color:#8ba4b8; border:1.5px solid #2b3a4a; }
  .tg-btn-outline:hover{ border-color:#4a6278; color:#e8f0f8; }
  .tg-label{ color:#8ba4b8; font-size:12px; font-weight:700; letter-spacing:.07em; text-transform:uppercase; display:block; margin-bottom:8px; }
  .tg-err{ display:flex; align-items:center; gap:6px; margin-top:7px; color:#ef5350; font-size:13px; }
  .tg-notice{ padding:12px 14px; border-radius:10px; font-size:13px; line-height:1.5; }
`;

export const CreatePostPage = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const communityFromUrl = searchParams.get('community');
  const [charCount, setCharCount] = useState(0);
  const [tagInput, setTagInput] = useState('');
  const [tags, setTags] = useState<string[]>([]);

  const { register, handleSubmit, formState: { errors }, watch, control, setValue } = useForm<PostFormData>({
    resolver: zodResolver(postSchema),
    defaultValues: { content: '', community: communityFromUrl || '', tags: [] },
  });

  const contentValue = watch('content', '');
  const selectedCommunity = watch('community', '');

  const { data: communitiesData, isLoading: commLoading } = useQuery({
    queryKey: ['communities'], queryFn: () => communitiesApi.list(),
  });

  useEffect(() => { if (communityFromUrl) setValue('community', communityFromUrl); }, [communityFromUrl, setValue]);

  const communitiesArray = Array.isArray(communitiesData) ? communitiesData : (communitiesData as any)?.results || [];
  const availableCommunities = communitiesArray.filter((c: any) => c.is_owner === true);

  useEffect(() => { setCharCount(contentValue?.length || 0); }, [contentValue]);
  useEffect(() => { setValue('tags', tags); }, [tags, setValue]);

  const createMutation = useMutation({
    mutationFn: postsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
      if (user?.id) queryClient.invalidateQueries({ queryKey: ['user-posts', user.id] });
      navigate('/posts');
    },
  });

  const addTag = () => {
    const t = tagInput.trim().toLowerCase();
    if (t && !tags.includes(t) && tags.length < 10) { setTags([...tags, t]); setTagInput(''); }
  };

  const onSubmit = (data: PostFormData) => {
    const payload: any = { content: data.content };
    if (data.community?.trim()) payload.community = data.community;
    if (tags.length > 0) payload.tags_list = tags;
    createMutation.mutate(payload);
  };

  const handleCancel = () => {
    if (contentValue?.length > 0) {
      if (window.confirm('Есть несохранённые изменения. Уйти?')) navigate('/posts');
    } else navigate('/posts');
  };

  return (
    <div style={{ minHeight: '100vh', background: '#17212b', fontFamily: "'SF Pro Display',-apple-system,BlinkMacSystemFont,sans-serif", padding: '24px 20px', maxWidth: '640px', margin: '0 auto' }}>
      <style>{S}</style>

      <button className="tg-btn tg-btn-outline" onClick={handleCancel} style={{ marginBottom: '24px' }}>
        <ArrowLeft size={16} /> Назад к постам
      </button>

      <div style={{ animation: 'fadeUp .3s ease' }}>
        <h1 style={{ color: '#e8f0f8', fontSize: '24px', fontWeight: '700', margin: '0 0 6px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <FileText size={22} color="#2196f3" /> Создать пост
        </h1>
        <p style={{ color: '#4a6278', fontSize: '14px', margin: '0 0 28px' }}>Поделитесь своими мыслями с сообществом</p>

        <form onSubmit={handleSubmit(onSubmit)}>

          {/* Community */}
          <div style={{ marginBottom: '20px' }}>
            <label className="tg-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Users size={12} /> Сообщество (необязательно)
            </label>
            <Controller
              name="community" control={control}
              render={({ field }) => (
                <select className="tg-select" {...field} disabled={commLoading}>
                  <option value="">👤 От моего имени (личный пост)</option>
                  {commLoading ? (
                    <option disabled>Загрузка...</option>
                  ) : availableCommunities.length === 0 ? (
                    <option disabled>Нет сообществ для публикации</option>
                  ) : (
                    availableCommunities.map((c: any) => (
                      <option key={c.id} value={c.id}>🏘️ {c.name}</option>
                    ))
                  )}
                </select>
              )}
            />
            <div className="tg-notice" style={{ marginTop: '8px', background: selectedCommunity ? 'rgba(33,150,243,.08)' : 'rgba(76,175,80,.08)', border: `1px solid ${selectedCommunity ? 'rgba(33,150,243,.2)' : 'rgba(76,175,80,.2)'}`, color: selectedCommunity ? '#90caf9' : '#a5d6a7' }}>
              {selectedCommunity ? '📌 Пост будет опубликован от имени сообщества.' : '✅ Пост будет опубликован от вашего имени.'}
            </div>
          </div>

          {/* Content */}
          <div style={{ marginBottom: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <label className="tg-label" style={{ margin: 0 }}>Содержание *</label>
              <span style={{ color: charCount < 10 ? '#ef5350' : charCount > 800 ? '#ff9800' : '#4a6278', fontSize: '12px' }}>{charCount}/1000</span>
            </div>
            <textarea
              className={`tg-textarea${errors.content ? ' err' : ''}`}
              {...register('content')}
              onChange={e => setCharCount(e.target.value.length)}
              placeholder="Что у вас на уме? Поделитесь мыслями..."
              rows={10}
              maxLength={1000}
            />
            {errors.content && <div className="tg-err"><AlertCircle size={13} />{errors.content.message}</div>}
            {!errors.content && charCount === 0 && (
              <div className="tg-notice" style={{ marginTop: '8px', background: 'rgba(33,150,243,.06)', border: '1px solid rgba(33,150,243,.15)', color: '#8ba4b8' }}>
                💡 Минимум 10 символов. Добавьте теги для лучшей видимости.
              </div>
            )}
          </div>

          {/* Tags */}
          <div style={{ marginBottom: '28px' }}>
            <label className="tg-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Hash size={12} /> Теги (необязательно, макс. 10)
            </label>
            <div style={{ display: 'flex', gap: '8px' }}>
              <input
                className="tg-input"
                type="text"
                value={tagInput}
                onChange={e => setTagInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addTag(); } }}
                placeholder="Введите тег и нажмите Enter"
                style={{ flex: 1 }}
              />
              <button type="button" className="tg-btn tg-btn-outline" onClick={addTag} disabled={!tagInput.trim() || tags.length >= 10} style={{ flexShrink: 0 }}>
                <Plus size={15} />
              </button>
            </div>
            {tags.length > 0 && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '10px', padding: '12px', background: '#242f3d', borderRadius: '10px', border: '1px solid #2b3a4a' }}>
                {tags.map(tag => (
                  <span key={tag} style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '4px 10px', borderRadius: '20px', fontSize: '13px', background: 'rgba(33,150,243,.1)', color: '#2196f3', border: '1px solid rgba(33,150,243,.2)' }}>
                    #{tag}
                    <button type="button" onClick={() => setTags(tags.filter(t => t !== tag))} style={{ background: 'none', border: 'none', color: '#2196f3', cursor: 'pointer', padding: 0, display: 'flex' }}>
                      <X size={12} />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Error */}
          {createMutation.isError && (
            <div className="tg-notice" style={{ marginBottom: '20px', background: 'rgba(244,67,54,.08)', border: '1px solid rgba(244,67,54,.25)', color: '#ef5350', display: 'flex', gap: '8px' }}>
              <AlertCircle size={16} style={{ flexShrink: 0, marginTop: '1px' }} /> Ошибка при создании поста. Попробуйте ещё раз.
            </div>
          )}

          {/* Buttons */}
          <div style={{ display: 'flex', gap: '10px' }}>
            <button type="submit" className="tg-btn tg-btn-primary" style={{ flex: 1, justifyContent: 'center' }} disabled={createMutation.isPending || charCount < 10}>
              {createMutation.isPending
                ? <><div style={{ width: '16px', height: '16px', border: '2px solid rgba(255,255,255,.3)', borderTop: '2px solid #fff', borderRadius: '50%', animation: 'spin .7s linear infinite' }} /> Публикация...</>
                : <><Send size={15} /> Опубликовать</>}
            </button>
            <button type="button" className="tg-btn tg-btn-outline" onClick={handleCancel} disabled={createMutation.isPending}>Отмена</button>
          </div>
        </form>

        {/* Live preview */}
        {charCount > 0 && (
          <div style={{ marginTop: '24px', padding: '18px', background: '#1e2c3a', border: '1px solid #2b3a4a', borderRadius: '14px' }}>
            <div style={{ color: '#4a6278', fontSize: '11px', fontWeight: '700', letterSpacing: '.07em', textTransform: 'uppercase', marginBottom: '12px' }}>👁 Предпросмотр</div>
            {selectedCommunity && (
              <div style={{ color: '#8ba4b8', fontSize: '12px', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Users size={11} /> От имени: <b style={{ color: '#e8f0f8' }}>{availableCommunities.find((c: any) => String(c.id) === selectedCommunity)?.name || 'Сообщество'}</b>
              </div>
            )}
            <p style={{ color: '#e8f0f8', fontSize: '14px', lineHeight: 1.65, margin: '0 0 12px', whiteSpace: 'pre-wrap' }}>{contentValue}</p>
            {tags.length > 0 && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {tags.map(t => <span key={t} style={{ padding: '3px 10px', borderRadius: '20px', fontSize: '12px', background: 'rgba(33,150,243,.1)', color: '#2196f3', border: '1px solid rgba(33,150,243,.2)' }}>#{t}</span>)}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
