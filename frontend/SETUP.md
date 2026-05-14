# 🚀 Инструкция по настройке Frontend проекта

## Шаг 1: Установка зависимостей

```bash
cd frontend
npm install
```

Это установит все необходимые пакеты:
- React, TypeScript, Vite
- React Router, React Query
- Axios
- Tailwind CSS, shadcn/ui компоненты
- React Hook Form, Zod

## Шаг 2: Настройка окружения

Создайте файл `.env` в директории `frontend/`:

```bash
echo "VITE_API_URL=http://localhost:8000" > .env
```

**Важно:** Если ваш Django backend работает на другом порту или домене, измените URL в `.env`.

## Шаг 3: Запуск проекта

```bash
npm run dev
```

Приложение будет доступно на `http://localhost:3000`

## Шаг 4: Настройка CORS в Django (если нужно)

Если возникают ошибки CORS, добавьте в Django `settings/base.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
CORS_ALLOW_CREDENTIALS = True
```

И установите `django-cors-headers`:
```bash
pip install django-cors-headers
```

## 📝 Основные команды

- `npm run dev` - Запуск dev сервера
- `npm run build` - Production сборка
- `npm run lint` - Проверка кода
- `npm run preview` - Предпросмотр production сборки

## 🔍 Структура проекта

```
frontend/
├── src/
│   ├── app/              # Инициализация приложения
│   ├── shared/           # Переиспользуемый код
│   │   ├── api/         # API клиенты
│   │   ├── components/  # UI компоненты
│   │   ├── lib/         # Утилиты
│   │   └── types/       # TypeScript типы
│   ├── features/        # Бизнес-логика
│   └── widgets/         # Составные компоненты
├── .env                 # Переменные окружения
└── package.json
```

## ✅ Готово!

После выполнения этих шагов проект будет готов к работе. Все компоненты интегрированы с Django backend API.

