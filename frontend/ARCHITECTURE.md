# Архитектура Frontend проекта

## 📁 Структура директорий (Feature-Sliced Design)

```
src/
├── app/                    # Инициализация приложения
│   ├── providers/          # React providers (Query, Router)
│   └── router/             # Конфигурация роутинга
│
├── shared/                 # Переиспользуемый код
│   ├── api/                # API клиенты для всех endpoints
│   │   ├── auth.api.ts
│   │   ├── users.api.ts
│   │   ├── posts.api.ts
│   │   ├── events.api.ts
│   │   ├── communities.api.ts
│   │   └── notifications.api.ts
│   ├── components/         # UI компоненты (shadcn/ui)
│   │   └── ui/
│   ├── hooks/              # Переиспользуемые хуки
│   ├── lib/                # Утилиты и конфигурация
│   │   ├── api.ts          # Axios instance с interceptors
│   │   └── utils.ts        # Вспомогательные функции
│   └── types/              # TypeScript типы и интерфейсы
│
├── features/               # Бизнес-логика по доменам
│   ├── auth/               # Авторизация
│   │   ├── context/        # AuthContext
│   │   ├── components/     # Login, Register, ProtectedRoute
│   │   └── pages/          # Страницы авторизации
│   ├── users/              # Пользователи
│   │   ├── components/     # UserCard, ProfileForm
│   │   ├── hooks/          # useUsers, useProfile
│   │   └── pages/          # ProfilePage, UsersListPage
│   ├── posts/              # Посты
│   │   ├── components/     # PostCard, PostForm, CommentList
│   │   ├── hooks/          # usePosts, useComments
│   │   └── pages/          # PostsListPage, PostDetailPage
│   ├── events/             # События
│   ├── communities/        # Сообщества
│   └── notifications/      # Уведомления
│
└── widgets/                # Составные компоненты
    └── layout/             # Layout, Header, Sidebar
```

## 🔑 Ключевые компоненты

### API Layer
- `shared/lib/api.ts` - Axios instance с автоматическим refresh токенов
- `shared/api/*.api.ts` - API клиенты для каждого домена

### Авторизация
- JWT токены (access + refresh)
- Автоматическое обновление токенов
- Protected routes
- AuthContext для глобального состояния

### UI Components
- shadcn/ui компоненты (Button, Input, Card, etc.)
- Адаптивный дизайн
- Темная тема (поддержка)

### Data Fetching
- React Query для кеширования и синхронизации
- Оптимистичные обновления
- Автоматический refetch

## 🚀 Особенности

1. **Type Safety** - Полная типизация всех API responses
2. **Error Handling** - Централизованная обработка ошибок
3. **Loading States** - Skeleton loaders и spinners
4. **Forms** - React Hook Form + Zod валидация
5. **Routing** - React Router с protected routes

