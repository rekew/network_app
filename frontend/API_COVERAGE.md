# 📡 Покрытие Backend API

## ✅ Все Django endpoints покрыты

### Авторизация (`/users/v1/user/`)
- ✅ `POST /users/v1/user/login/` - Вход
- ✅ `POST /users/v1/user/register/` - Регистрация
- ✅ `GET /users/v1/user/personal_data/` - Текущий пользователь

### Токены
- ✅ `POST /token/` - Получение токенов
- ✅ `POST /token/refresh/` - Обновление access token
- ✅ `POST /token/verify/` - Проверка токена

### Пользователи (`/users/api/`)
- ✅ `GET /users/api/` - Список пользователей
- ✅ `GET /users/api/{id}/` - Детали пользователя

### Посты (`/posts/api/`)
- ✅ `GET /posts/api/` - Список постов
- ✅ `GET /posts/api/{id}/` - Детали поста
- ✅ `POST /posts/api/` - Создание поста
- ✅ `PUT /posts/api/{id}/` - Обновление поста
- ✅ `DELETE /posts/api/{id}/` - Удаление поста

### События (`/events/api/`)
- ✅ `GET /events/api/` - Список событий
- ✅ `GET /events/api/{id}/` - Детали события
- ✅ `POST /events/api/` - Создание события
- ✅ `PUT /events/api/{id}/` - Обновление события
- ✅ `DELETE /events/api/{id}/` - Удаление события

### Сообщества (`/communities/api/`)
- ✅ `GET /communities/api/` - Список сообществ
- ✅ `GET /communities/api/{id}/` - Детали сообщества
- ✅ `POST /communities/api/` - Создание сообщества
- ✅ `PUT /communities/api/{id}/` - Обновление сообщества
- ✅ `DELETE /communities/api/{id}/` - Удаление сообщества

### Уведомления (`/notification/`)
- ✅ `GET /notification/` - Список уведомлений
- ✅ `POST /notification/` - Создание уведомления

## 📝 Типы данных

Все модели Django имеют соответствующие TypeScript типы:
- `User`, `Profile`, `Media`
- `Post`, `Comment`, `Tag`
- `Community`, `CommunityMembership`
- `Event`, `EventApplication`
- `Notification`
- `Report`

## 🔄 Автоматические возможности

- ✅ JWT токены автоматически добавляются в заголовки
- ✅ Access token автоматически обновляется при истечении
- ✅ Автоматический logout при ошибках авторизации
- ✅ React Query кеширует все запросы
- ✅ Автоматический refetch при мутациях

## 💡 Примеры использования

### Использование API в компонентах

```typescript
import { useQuery, useMutation } from '@tanstack/react-query';
import { postsApi } from '@/shared/api';

// Получение данных
const { data, isLoading } = useQuery({
  queryKey: ['posts'],
  queryFn: () => postsApi.list(),
});

// Создание данных
const mutation = useMutation({
  mutationFn: postsApi.create,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['posts'] });
  },
});
```

Все готово к использованию! 🚀

