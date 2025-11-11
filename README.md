# Control System - Микросервисная архитектура

Система управления пользователями и заказами на основе микросервисной архитектуры с использованием FastAPI, PostgreSQL и Docker.

## Описание проекта

Проект представляет собой распределенную систему из трех микросервисов:

- **API Gateway** - единая точка входа для клиентских приложений
- **Service Users** - управление пользователями и аутентификация
- **Service Orders** - управление заказами

Все сервисы взаимодействуют через REST API и используют JWT для авторизации. Коммуникация между сервисами защищена и недоступна извне.

## Архитектура

```
Клиент
   |
   | HTTP (port 8000)
   v
API Gateway -----> Service Users (port 8001) ---\
   |                                              |
   +-------------> Service Orders (port 8002) ----+--> PostgreSQL
                                                  |
                                                  \--> users_db
                                                  \--> orders_db
```

### Компоненты

#### 1. API Gateway (порт 8000)

Единственный сервис, доступный извне. Отвечает за:
- Маршрутизацию запросов к микросервисам
- Валидацию JWT токенов
- Проксирование запросов к внутренним сервисам
- Унифицированную обработку ошибок

**Эндпоинты:**
- `POST /v1/users/register` - регистрация пользователя
- `POST /v1/users/login` - авторизация
- `GET /v1/users/me` - профиль текущего пользователя
- `PUT /v1/users/me` - обновление профиля
- `GET /v1/users/all` - список пользователей (admin)
- `POST /v1/orders/create` - создание заказа
- `GET /v1/orders/my` - список заказов пользователя
- `GET /v1/orders/{order_id}` - получение заказа
- `PUT /v1/orders/{order_id}/status` - обновление статуса
- `DELETE /v1/orders/{order_id}` - отмена заказа

#### 2. Service Users (порт 8001)

Внутренний сервис для управления пользователями:
- Регистрация и аутентификация
- Хранение данных пользователей
- Генерация JWT токенов
- Управление ролями (admin, client)

**База данных:** `users_db`

#### 3. Service Orders (порт 8002)

Внутренний сервис для управления заказами:
- Создание и управление заказами
- Автоматический расчет итоговой суммы
- Отслеживание статусов заказов
- Проверка прав доступа

**База данных:** `orders_db`

**Статусы заказов:**
- `CREATED` - создан
- `IN_PROGRESS` - в работе
- `COMPLETED` - выполнен
- `CANCELLED` - отменён

## Технологический стек

- **Backend:** Python 3.11, FastAPI
- **Database:** PostgreSQL 15
- **Authentication:** JWT (python-jose)
- **Password Hashing:** bcrypt
- **HTTP Client:** httpx (для межсервисной коммуникации)
- **Validation:** Pydantic
- **Containerization:** Docker, Docker Compose

## Требования

- Docker >= 20.10
- Docker Compose >= 2.0
- (Опционально) Python 3.11+ для локальной разработки

## Быстрый старт с Docker

### 1. Клонирование и настройка

```bash
git clone https://github.com/Kemuni/control_system_prak2.git
cd control_system_prak2

# Копирование и настройка переменных окружения
cp .env.example .env
```

### 2. Настройка переменных окружения

Отредактируйте `.env` файл и измените следующие значения:

```env
POSTGRES_PASSWORD=your_secure_password
JWT_SECRET_KEY=your_very_long_secret_key_min_32_characters
```

### 3. Запуск сервисов

```bash
# Сборка и запуск всех контейнеров
docker-compose up --build -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

### 4. Проверка работоспособности

```bash
curl http://localhost:8000/health
# Ожидаемый ответ: {"status":"healthy"}
```


### Настройка окружения

Создайте `.env` файл в корне проекта:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_TOKEN_EXPIRE_MINUTES=30

SERVICE_USERS_HOST=localhost
SERVICE_USERS_PORT=8001

SERVICE_ORDERS_HOST=localhost
SERVICE_ORDERS_PORT=8002

API_GATEWAY_HOST=localhost
API_GATEWAY_PORT=8000

SERVICE_USERS_URL=http://localhost:8001
SERVICE_ORDERS_URL=http://localhost:8002
```

### Запуск сервисов для локальной разработки

```bash
# Terminal 1 - Service Users
cd service_users
python main.py

# Terminal 2 - Service Orders
cd service_orders
python main.py

# Terminal 3 - API Gateway
cd api_gateway
python main.py
```

## Использование API

### Регистрация пользователя

```bash
curl -X POST http://localhost:8000/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "name": "John Doe",
    "roles": ["client"]
  }'
```

### Авторизация

```bash
curl -X POST http://localhost:8000/v1/users/login \
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
    "access_token": "eyJhbGc...",
    "token_type": "bearer"
  }
}
```

## Документация API

После запуска сервисов документация доступна по адресам:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Структура проекта

```
control_system_prak2/
├── api_gateway/               # API Gateway сервис
│   ├── routers/
│   │   ├── users.py          # Роуты для пользователей
│   │   └── orders.py         # Роуты для заказов
│   ├── auth.py               # JWT валидация
│   ├── config.py             # Конфигурация
│   ├── schemas.py            # Pydantic модели
│   ├── main.py               # Точка входа
│   ├── Dockerfile
│   └── requirements.txt
│
├── service_users/            # Сервис пользователей
│   ├── routers/
│   │   ├── auth.py          # Регистрация/авторизация
│   │   └── users.py         # Управление пользователями
│   ├── auth.py              # JWT логика
│   ├── config.py            # Конфигурация
│   ├── database.py          # БД подключение
│   ├── models.py            # SQLAlchemy модели
│   ├── schemas.py           # Pydantic модели
│   ├── main.py              # Точка входа
│   ├── Dockerfile
│   └── requirements.txt
│
├── service_orders/           # Сервис заказов
│   ├── routers/
│   │   └── orders.py        # CRUD для заказов
│   ├── auth.py              # JWT валидация
│   ├── config.py            # Конфигурация
│   ├── database.py          # БД подключение
│   ├── models.py            # SQLAlchemy модели
│   ├── schemas.py           # Pydantic модели
│   ├── main.py              # Точка входа
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml        # Оркестрация сервисов
├── init-db.sql              # Инициализация БД
├── .env                     # Переменные окружения
├── .env.docker              # Шаблон для Docker
├── .dockerignore            # Исключения Docker
├── DOCKER_README.md         # Docker документация
└── README.md                # Этот файл
```

## Модели данных

### User (Пользователь)

```python
{
  "id": "UUID",
  "email": "string",
  "name": "string",
  "roles": ["admin" | "client"],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Order (Заказ)

```python
{
  "id": "UUID",
  "user_id": "UUID",
  "items": [
    {
      "name": "string",
      "amount": "integer",
      "description": "string",
      "price": "decimal"
    }
  ],
  "status": "CREATED" | "IN_PROGRESS" | "COMPLETED" | "CANCELLED",
  "total_amount": "decimal",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```
