# API Gateway

API Gateway для микросервисной архитектуры. Проксирует запросы к сервисам Users и Orders с проверкой JWT токенов на защищенных эндпоинтах.

## Архитектура

API Gateway выступает единой точкой входа для клиентских приложений и проксирует запросы к следующим микросервисам:
- **service_users** (порт 8001) - управление пользователями и аутентификация
- **service_orders** (порт 8002) - управление заказами

## Маппинг эндпоинтов

### Users Service

| API Gateway | Service Users | Авторизация | Описание |
|-------------|---------------|-------------|----------|
| POST /v1/users/register | POST /v1/auth/register | Нет | Регистрация пользователя |
| POST /v1/users/login | POST /v1/auth/login | Нет | Авторизация пользователя |
| GET /v1/users/me | GET /v1/users/me | Да | Получить профиль |
| PUT /v1/users/me | PUT /v1/users/me | Да | Обновить профиль |
| GET /v1/users/all | GET /v1/users/ | Да | Список пользователей (admin) |

### Orders Service

| API Gateway | Service Orders | Авторизация | Описание |
|-------------|----------------|-------------|----------|
| POST /v1/orders/create | POST /v1/orders/ | Да | Создать заказ |
| GET /v1/orders/my | GET /v1/orders/ | Да | Список заказов пользователя |
| GET /v1/orders/{order_id} | GET /v1/orders/{order_id} | Да | Получить заказ по ID |
| PUT /v1/orders/{order_id}/status | PUT /v1/orders/{order_id}/status | Да | Обновить статус заказа |
| DELETE /v1/orders/{order_id} | DELETE /v1/orders/{order_id} | Да | Отменить заказ |

## Функционал

### Проксирование запросов
- Прозрачная передача запросов к внутренним микросервисам
- Автоматическая передача JWT токенов в заголовках
- Обработка ошибок от сервисов

### Авторизация
- Проверка JWT токенов на защищенных эндпоинтах
- Публичные эндпоинты: регистрация и авторизация
- Все остальные эндпоинты требуют валидный JWT токен

### Обработка ошибок
- Унифицированный формат ответов об ошибках
- Валидация входных данных с Pydantic
- Обработка недоступности микросервисов

## Установка и запуск

### 1. Установите зависимости

```bash
pip install -r requirements.txt
```

### 2. Настройте переменные окружения

```bash
cp .env.example ../.env
# Отредактируйте ../.env файл с вашими настройками
```

**Важно:** JWT_SECRET_KEY должен совпадать с тем, что используется в service_users и service_orders!

### 3. Запустите микросервисы

Перед запуском API Gateway убедитесь, что запущены:
- service_users на порту 8001
- service_orders на порту 8002

### 4. Запустите API Gateway

```bash
python main.py
```

API Gateway будет доступен по адресу: http://localhost:8000

## Документация API

После запуска документация доступна по адресам:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Swagger содержит полное описание всех эндпоинтов, схем запросов и ответов.

## Использование

### 1. Регистрация пользователя

```bash
curl -X POST "http://localhost:8000/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "name": "John Doe",
    "roles": ["client"]
  }'
```

### 2. Авторизация

```bash
curl -X POST "http://localhost:8000/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

Ответ содержит JWT токен:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

### 3. Использование токена

Для защищенных эндпоинтов передавайте токен в заголовке:

```bash
curl -X GET "http://localhost:8000/v1/users/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 4. Создание заказа

```bash
curl -X POST "http://localhost:8000/v1/orders/create" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "name": "Товар 1",
        "amount": 2,
        "description": "Описание товара",
        "price": 100.50
      }
    ]
  }'
```

## Health Check

API Gateway предоставляет эндпоинты для проверки состояния:
- `GET /` - информация о сервисе
- `GET /health` - health check

## Структура проекта

```
api_gateway/
├── routers/
│   ├── __init__.py
│   ├── users.py          # Роутер для users service
│   └── orders.py         # Роутер для orders service
├── __init__.py
├── auth.py               # JWT валидация
├── config.py             # Настройки приложения
├── errors.py             # Кастомные исключения
├── main.py               # Главный файл приложения
├── schemas.py            # Pydantic схемы для документации
├── requirements.txt      # Зависимости
├── .env.example          # Пример конфигурации
├── .gitignore
└── README.md
```

## Безопасность

- JWT токены валидируются на стороне API Gateway
- Токены не передаются клиенту после проверки
- CORS настроен для работы с любыми источниками (настройте для production)
- Все защищенные эндпоинты требуют валидный JWT токен

## Мониторинг и логирование

- Логирование ошибок при недоступности микросервисов
- Структурированные ошибки в едином формате
- Таймауты для запросов к микросервисам (30 секунд)

## Production готовность

Для production окружения рекомендуется:
1. Настроить CORS с конкретными доменами
2. Использовать HTTPS
3. Добавить rate limiting
4. Настроить централизованное логирование
5. Добавить метрики и мониторинг
6. Использовать переменные окружения для sensitive данных
7. Настроить таймауты и retry политики
