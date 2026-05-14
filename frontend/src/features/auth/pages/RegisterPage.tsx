import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const RegisterPage = () => {
  const [formData, setFormData] = useState({ email: '', username: '', full_name: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(formData.email, formData.username, formData.full_name, formData.password);
      navigate('/');
    } catch (err: any) {
      const data = err.response?.data || {};
      let msg = 'Ошибка регистрации';
      if (data.detail) msg = data.detail;
      else if (typeof data === 'object') {
        const firstKey = Object.keys(data)[0];
        if (Array.isArray(data[firstKey])) msg = data[firstKey][0];
        else if (typeof data[firstKey] === 'string') msg = data[firstKey];
      }
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const fields = [
    { name: 'email', label: 'Email', type: 'email', placeholder: 'example@mail.com' },
    { name: 'username', label: 'Имя пользователя', type: 'text', placeholder: 'username' },
    { name: 'full_name', label: 'Полное имя', type: 'text', placeholder: 'Иван Иванов' },
    { name: 'password', label: 'Пароль', type: 'password', placeholder: '••••••••' },
  ];

  return (
    <div style={{
      minHeight: '100vh',
      background: '#17212b',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: "'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif",
      padding: '16px',
    }}>
      <div style={{ width: '100%', maxWidth: '380px', animation: 'fadeUp 0.4s ease' }}>
        <style>{`
          @keyframes fadeUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
          }
          .tg-input {
            width: 100%;
            background: #242f3d;
            border: 1.5px solid #2b3a4a;
            border-radius: 10px;
            padding: 13px 16px;
            color: #e8f0f8;
            font-size: 15px;
            outline: none;
            transition: border-color 0.2s;
            box-sizing: border-box;
            font-family: inherit;
          }
          .tg-input::placeholder { color: #4a6278; }
          .tg-input:focus { border-color: #2196f3; }
          .tg-btn {
            width: 100%;
            background: #2196f3;
            color: #fff;
            border: none;
            border-radius: 10px;
            padding: 14px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s, transform 0.1s;
            font-family: inherit;
          }
          .tg-btn:hover:not(:disabled) { background: #1e88e5; }
          .tg-btn:active:not(:disabled) { transform: scale(0.98); }
          .tg-btn:disabled { opacity: 0.5; cursor: not-allowed; }
        `}</style>

        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{
            width: '72px', height: '72px',
            background: 'linear-gradient(135deg, #2196f3, #1565c0)',
            borderRadius: '24px',
            display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
            marginBottom: '20px',
            boxShadow: '0 8px 32px rgba(33,150,243,0.25)',
          }}>
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none">
              <path d="M20 2H4C2.9 2 2 2.9 2 4v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z" fill="white"/>
            </svg>
          </div>
          <h1 style={{ color: '#e8f0f8', fontSize: '24px', fontWeight: '700', margin: '0 0 6px' }}>
            Создать аккаунт
          </h1>
          <p style={{ color: '#4a6278', fontSize: '14px', margin: 0 }}>
            Зарегистрируйтесь бесплатно
          </p>
        </div>

        {/* Form */}
        <div style={{
          background: '#1e2c3a',
          borderRadius: '16px',
          padding: '28px',
          border: '1px solid #2b3a4a',
        }}>
          {error && (
            <div style={{
              background: 'rgba(244,67,54,0.1)',
              border: '1px solid rgba(244,67,54,0.3)',
              borderRadius: '8px',
              padding: '12px 14px',
              color: '#ef5350',
              fontSize: '13px',
              marginBottom: '20px',
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {fields.map((field, i) => (
              <div key={field.name} style={{ marginBottom: i === fields.length - 1 ? '24px' : '14px' }}>
                <label style={{ color: '#8ba4b8', fontSize: '12px', fontWeight: '600', letterSpacing: '0.06em', textTransform: 'uppercase', display: 'block', marginBottom: '8px' }}>
                  {field.label}
                </label>
                <input
                  className="tg-input"
                  name={field.name}
                  type={field.type}
                  placeholder={field.placeholder}
                  value={formData[field.name as keyof typeof formData]}
                  onChange={handleChange}
                  required
                  minLength={field.name === 'password' ? 8 : undefined}
                />
              </div>
            ))}

            <button className="tg-btn" type="submit" disabled={loading}>
              {loading ? 'Регистрация...' : 'Зарегистрироваться'}
            </button>
          </form>
        </div>

        <p style={{ textAlign: 'center', color: '#4a6278', fontSize: '14px', marginTop: '20px' }}>
          Уже есть аккаунт?{' '}
          <Link to="/login" style={{ color: '#2196f3', textDecoration: 'none', fontWeight: '600' }}>
            Войти
          </Link>
        </p>
      </div>
    </div>
  );
};