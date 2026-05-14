import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { communitiesApi } from '@/shared/api';
import { ArrowLeft, Globe, Lock, Eye, Users, AlertCircle } from 'lucide-react';
import { useState, useEffect } from 'react';

const communitySchema = z.object({
  name: z.string().min(3, 'Минимум 3 символа').max(100, 'Максимум 100 символов'),
  description: z.string().max(500, 'Максимум 500 символов').optional(),
  visibility: z.enum(['public', 'private', 'secret']).default('public'),
});
type CommunityFormData = z.infer<typeof communitySchema>;

const S = `
  @keyframes fadeUp { from { opacity:0; transform:translateY(16px); } to { opacity:1; transform:translateY(0); } }
  .tg-input, .tg-textarea {
    width: 100%; background: #242f3d; border: 1.5px solid #2b3a4a; border-radius: 10px;
    padding: 13px 16px; color: #e8f0f8; font-size: 15px; outline: none;
    transition: border-color 0.2s; box-sizing: border-box; font-family: inherit;
  }
  .tg-input::placeholder, .tg-textarea::placeholder { color: #4a6278; }
  .tg-input:focus, .tg-textarea:focus { border-color: #2196f3; }
  .tg-input.error, .tg-textarea.error { border-color: #f44336; }
  .tg-textarea { resize: none; }
  .tg-btn {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 13px 20px; border-radius: 10px; font-size: 15px; font-weight: 600;
    cursor: pointer; border: none; transition: all 0.2s; font-family: inherit;
  }
  .tg-btn-primary { background: #2196f3; color: #fff; }
  .tg-btn-primary:hover:not(:disabled) { background: #1e88e5; }
  .tg-btn-primary:disabled { opacity: 0.45; cursor: not-allowed; }
  .tg-btn-outline { background: transparent; color: #8ba4b8; border: 1.5px solid #2b3a4a; }
  .tg-btn-outline:hover { border-color: #4a6278; color: #e8f0f8; }
  .vis-option {
    padding: 14px 16px; border-radius: 12px; border: 1.5px solid #2b3a4a;
    cursor: pointer; transition: all 0.2s; background: #242f3d; text-align: left;
    font-family: inherit;
  }
  .vis-option:hover { border-color: #4a6278; }
`;

const visOptions = [
  { value: 'public',  label: 'Публичное',  desc: 'Любой может вступить',           Icon: Globe, color: '#4caf50' },
  { value: 'private', label: 'Приватное', desc: 'Требуется одобрение',           Icon: Lock,  color: '#ff9800' },
  { value: 'secret',  label: 'Секретное', desc: 'Только по приглашению',         Icon: Eye,   color: '#f44336' },
];

export const CreateCommunityPage = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [charCount, setCharCount] = useState(0);

  const { register, handleSubmit, formState: { errors }, watch, setValue } = useForm<CommunityFormData>({
    resolver: zodResolver(communitySchema),
    defaultValues: { name: '', description: '', visibility: 'public' },
  });

  const nameValue = watch('name', '');
  const visibilityValue = watch('visibility', 'public');
  const descriptionValue = watch('description', '');

  useEffect(() => setCharCount(descriptionValue?.length || 0), [descriptionValue]);

  const createMutation = useMutation({
    mutationFn: communitiesApi.create,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['communities'] });
      navigate(`/communities/${data.id}`);
    },
  });

  const handleCancel = () => {
    if (nameValue || descriptionValue) {
      if (window.confirm('Есть несохранённые изменения. Уйти?')) navigate('/communities');
    } else {
      navigate('/communities');
    }
  };

  return (
    <div style={{
      minHeight: '100vh', background: '#17212b',
      fontFamily: "'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif",
      padding: '24px 20px', maxWidth: '560px', margin: '0 auto',
    }}>
      <style>{S}</style>

      <button className="tg-btn tg-btn-outline" onClick={handleCancel} style={{ marginBottom: '24px' }}>
        <ArrowLeft size={16} /> Назад
      </button>

      <div style={{ animation: 'fadeUp 0.3s ease' }}>
        <h1 style={{ color: '#e8f0f8', fontSize: '24px', fontWeight: '700', margin: '0 0 6px' }}>
          Создать сообщество
        </h1>
        <p style={{ color: '#4a6278', fontSize: '14px', margin: '0 0 28px' }}>
          Объедините людей вокруг общих интересов
        </p>

        <form onSubmit={handleSubmit(data => createMutation.mutate(data))}>
          {/* Name */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ color: '#8ba4b8', fontSize: '12px', fontWeight: '700', letterSpacing: '0.07em', textTransform: 'uppercase', display: 'block', marginBottom: '8px' }}>
              Название *
            </label>
            <input
              className={`tg-input${errors.name ? ' error' : ''}`}
              {...register('name')}
              placeholder="Название сообщества"
              maxLength={100}
            />
            {errors.name && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '8px', color: '#ef5350', fontSize: '13px' }}>
                <AlertCircle size={13} /> {errors.name.message}
              </div>
            )}
          </div>

          {/* Description */}
          <div style={{ marginBottom: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <label style={{ color: '#8ba4b8', fontSize: '12px', fontWeight: '700', letterSpacing: '0.07em', textTransform: 'uppercase' }}>
                Описание
              </label>
              <span style={{ color: charCount > 450 ? '#ff9800' : '#4a6278', fontSize: '12px' }}>
                {charCount}/500
              </span>
            </div>
            <textarea
              className={`tg-textarea${errors.description ? ' error' : ''}`}
              {...register('description')}
              onChange={e => setCharCount(e.target.value.length)}
              placeholder="Расскажите о сообществе..."
              rows={4}
              maxLength={500}
            />
          </div>

          {/* Visibility */}
          <div style={{ marginBottom: '28px' }}>
            <label style={{ color: '#8ba4b8', fontSize: '12px', fontWeight: '700', letterSpacing: '0.07em', textTransform: 'uppercase', display: 'block', marginBottom: '10px' }}>
              Видимость *
            </label>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {visOptions.map(({ value, label, desc, Icon, color }) => {
                const active = visibilityValue === value;
                return (
                  <button
                    key={value}
                    type="button"
                    className="vis-option"
                    onClick={() => setValue('visibility', value as any)}
                    style={{ borderColor: active ? color : '#2b3a4a', background: active ? `${color}10` : '#242f3d' }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div style={{
                        width: '36px', height: '36px', borderRadius: '10px', flexShrink: 0,
                        background: active ? `${color}20` : '#1e2c3a',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        color: active ? color : '#4a6278',
                      }}>
                        <Icon size={18} />
                      </div>
                      <div>
                        <div style={{ color: active ? color : '#e8f0f8', fontWeight: '600', fontSize: '14px' }}>{label}</div>
                        <div style={{ color: '#4a6278', fontSize: '12px', marginTop: '2px' }}>{desc}</div>
                      </div>
                      {active && (
                        <div style={{ marginLeft: 'auto', width: '20px', height: '20px', borderRadius: '50%', background: color, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          <svg width="10" height="8" viewBox="0 0 10 8" fill="none">
                            <path d="M1 4l3 3 5-6" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
                          </svg>
                        </div>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
            <input type="hidden" {...register('visibility')} />
          </div>

          {/* Error */}
          {createMutation.isError && (
            <div style={{ background: 'rgba(244,67,54,0.1)', border: '1px solid rgba(244,67,54,0.3)', borderRadius: '10px', padding: '14px', color: '#ef5350', fontSize: '13px', marginBottom: '20px', display: 'flex', gap: '8px' }}>
              <AlertCircle size={16} style={{ flexShrink: 0, marginTop: '1px' }} />
              Ошибка при создании. Попробуйте ещё раз.
            </div>
          )}

          {/* Buttons */}
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              type="submit"
              className="tg-btn tg-btn-primary"
              style={{ flex: 1, justifyContent: 'center' }}
              disabled={createMutation.isPending || !nameValue || nameValue.length < 3}
            >
              {createMutation.isPending ? (
                <>
                  <div style={{ width: '16px', height: '16px', border: '2px solid rgba(255,255,255,0.3)', borderTop: '2px solid #fff', borderRadius: '50%', animation: 'spin 0.7s linear infinite' }} />
                  Создание...
                </>
              ) : (
                <><Users size={16} /> Создать</>
              )}
            </button>
            <button type="button" className="tg-btn tg-btn-outline" onClick={handleCancel} disabled={createMutation.isPending}>
              Отмена
            </button>
          </div>
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </form>
      </div>
    </div>
  );
};