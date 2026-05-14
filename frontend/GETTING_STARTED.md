# 🚀 Руководство по запуску Frontend проекта

## Быстрый старт

### 1. Установка зависимостей

```bash
cd frontend
npm install
```

### 2. Настройка окружения

Создайте файл `.env` в директории `frontend/`:

```env
VITE_API_URL=http://localhost:8000
```

**Важно:** Обновите `VITE_API_URL` если ваш Django сервер работает на другом порту или домене.

### 3. Запуск проекта

```bash
npm run dev
```

Приложение откроется на `http://localhost:3000`

### 4. Сборка для production

```bash
npm run build
```

Собранные файлы будут в директории `dist/`

## 📋 Структура проекта

Проект использует **Feature-Sliced Design** архитектуру:

### `src/shared/` - Переиспользуемый код
- **api/** - API клиенты для всех Django endpoints
- **components/ui/** - UI компоненты (Button, Input, Card и т.д.)
- **lib/** - Утилиты (api.ts с interceptors, utils.ts)
- **types/** - TypeScript типы для всех моделей

### `src/features/` - Бизнес-логика
Каждая feature содержит:
- **components/** - Компоненты feature
- **hooks/** - React Query хуки
- **pages/** - Страницы

### `src/widgets/` - Составные компоненты
- **layout/** - Layout, Header, Sidebar, Navigation

## 🔧 Конфигурация

### Изменение API URL

Отредактируйте файл `.env`:
```env
VITE_API_URL=http://your-backend-url:port
```

Или установите переменную окружения:
```bash
export VITE_API_URL=http://your-backend-url:port
npm run dev
```

### Добавление новых API endpoints

1. Добавьте метод в соответствующий файл `src/shared/api/*.api.ts`
2. Создайте React Query hook в `src/features/*/hooks/`
3. Используйте hook в компонентах

Пример:
```typescript
// src/shared/api/posts.api.ts
export const postsApi = {
  // ... существующие методы
  newMethod: (): Promise<Data> =>
    apiClient.get('/posts/api/new-endpoint/'),
};
```

## 🎨 UI Компоненты

Проект использует shadcn/ui компоненты. Для добавления новых:

1. Скопируйте компонент из [shadcn/ui](https://ui.shadcn.com)
2. Поместите в `src/shared/components/ui/`
3. Импортируйте и используйте

## 📝 Основные endpoints

Все API endpoints покрыты в `src/shared/api/`:

- **Auth**: `/users/v1/user/login/`, `/users/v1/user/register/`
- **Users**: `/users/api/`, `/users/api/{id}/`
- **Posts**: `/posts/api/`, `/posts/api/{id}/`
- **Events**: `/events/api/`, `/events/api/{id}/`
- **Communities**: `/communities/api/`, `/communities/api/{id}/`
- **Notifications**: `/notification/`
- **Tokens**: `/token/`, `/token/refresh/`, `/token/verify/`

## 🔐 Авторизация

Система авторизации работает автоматически:
- JWT токены сохраняются в localStorage
- Access token автоматически добавляется в заголовки
- Refresh token обновляет access token при истечении
- Автоматический logout при ошибках авторизации

## 📦 Дополнительные команды

```bash
npm run lint      # Проверка кода
npm run build     # Production сборка
npm run preview   # Предпросмотр production сборки
```

## 🐛 Troubleshooting

### Ошибка подключения к API
- Проверьте, что Django сервер запущен
- Проверьте `VITE_API_URL` в `.env`
- Проверьте CORS настройки в Django

### Ошибки авторизации
- Очистите localStorage
- Проверьте, что токены сохраняются после логина
- Проверьте формат ответа от Django API

