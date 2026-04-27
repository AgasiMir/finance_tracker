# Finance Tracker API

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue)
![Redis](https://img.shields.io/badge/Redis-7-red)
![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen)
![License](https://img.shields.io/badge/license-MIT-yellow)

Мощный и масштабируемый REST API для управления личными финансами с поддержкой кошельков, операций и пользователей. Построен на современном стеке Python с использованием асинхронных технологий.

## 🚀 Особенности

- **Полностью асинхронный** - FastAPI + async/await для высокой производительности
- **Чистая архитектура** - разделение на слои (API, сервисы, репозитории, модели)
- **Unit of Work** - паттерн для управления транзакциями
- **Кэширование Redis** - для ускорения частых запросов
- **JWT аутентификация** - безопасный доступ к API
- **Лимитирование запросов** - защита от DDoS атак
- **Пагинация и фильтрация** - для работы с большими объемами данных
- **Миграции базы данных** - Alembic для управления схемой БД
- **Высокое тестовое покрытие** - 94% покрытие кода тестами
- **Docker контейнеризация** - готовность к деплою

## 📦 Технологический стек

- **Python 3.12** - основной язык программирования
- **FastAPI** - веб-фреймворк для построения API
- **SQLAlchemy 2.0** - ORM для работы с базой данных
- **PostgreSQL** - основная реляционная база данных
- **Redis** - кэширование и хранение сессий
- **Pydantic** - валидация данных и схемы
- **Alembic** - миграции базы данных
- **JWT** - аутентификация и авторизация
- **Docker & Docker Compose** - контейнеризация
- **pytest** - тестирование с покрытием
- **uv** - современный менеджер пакетов Python

## 🏗️ Архитектура

Проект следует принципам чистой архитектуры с четким разделением ответственности:

```
app/
├── api/              # Маршруты и обработчики HTTP-запросов
│   ├── v1/          # API версии 1
│   └── dependencies.py
├── core/            # Ядро приложения (настройки БД)
├── models/          # SQLAlchemy модели
├── repository/      # Репозитории для доступа к данным
├── services/        # Бизнес-логика
├── schemas/         # Pydantic схемы для валидации
├── uow/             # Unit of Work паттерн
├── utils/           # Вспомогательные утилиты
├── connectors/      # Коннекторы к внешним сервисам (Redis)
└── exceptions/      # Кастомные исключения
```

## 🚀 Быстрый старт

### Предварительные требования

- **Python 3.12** или выше
- **Docker и Docker Compose** (рекомендуется для простоты)
- **PostgreSQL 17** (если запускаете без Docker)
- **Redis 7** (если запускаете без Docker)
- **uv** - современный менеджер пакетов Python (установите через `pip install uv`)

### Настройка переменных окружения

Перед запуском необходимо настроить переменные окружения. Скопируйте пример конфигурации:

```bash
cp .env.example .env.dev
```

Отредактируйте `.env.dev` файл, указав свои настройки:

```env
# Окружение: DEV, TEST, PROD
ENVIRONMENT=DEV

# Настройки PostgreSQL
DB_DRIVER=postgresql+asyncpg
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=6432
DB_NAME=finance_tracker

# Настройки Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT настройки
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
```

### Запуск с Docker Compose (рекомендуется)

Docker Compose автоматически запустит все необходимые сервисы:

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd finance-tracker
```

2. Настройте переменные окружения (см. выше)

3. Запустите все сервисы:
```bash
docker-compose up -d
```

4. Проверьте, что все сервисы работают:
```bash
docker-compose ps
```

5. Примените миграции базы данных:
```bash
docker-compose exec app uv run alembic upgrade head
```

Приложение будет доступно по адресу: `http://localhost:8000`

**Запущенные сервисы:**
- **Приложение**: `http://localhost:8000`
- **PostgreSQL**: `localhost:6432`
- **Redis**: `localhost:6379`
- **RedisInsight** (GUI для Redis): `http://localhost:5540`

### Запуск без Docker (для разработки)

1. Установите uv (если еще не установлен):
```bash
pip install uv
```

2. Установите зависимости проекта:
```bash
uv sync --dev
```

3. Запустите PostgreSQL и Redis:
   - Установите PostgreSQL 17 и создайте базу `finance_tracker`
   - Установите Redis 7 и запустите сервер

4. Примените миграции:
```bash
uv run alembic upgrade head
```

5. Запустите приложение в режиме разработки:
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. Для тестирования запустите тесты:
```bash
uv run pytest
```

### Запуск в production

Для production использования рекомендуется:

1. Создать `.env.prod` с production настройками
2. Использовать Docker Compose production конфигурацию
3. Настроить reverse proxy (nginx) с SSL/TLS
4. Включить мониторинг и логирование

Пример production Docker команды:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📚 API Документация и тестирование

FastAPI автоматически генерирует полную интерактивную документацию API на основе Pydantic-схем и декораторов эндпоинтов. После запуска приложения доступны:

### Автоматически сгенерированная документация

- **Swagger UI**: `http://localhost:8000/docs` - интерактивная документация с возможностью тестирования API прямо в браузере
  - Позволяет отправлять реальные запросы к API
  - Отображает схемы запросов и ответов
  - Включает авторизацию через JWT токены
  - Показывает примеры кода для различных языков

- **ReDoc**: `http://localhost:8000/redoc` - альтернативная, более читаемая документация
  - Чистый и минималистичный интерфейс
  - Удобна для изучения структуры API
  - Автоматическая группировка эндпоинтов по тегам

- **OpenAPI спецификация**: `http://localhost:8000/openapi.json` - машинно-читаемая спецификация API
  - Может быть импортирована в Postman, Insomnia и другие инструменты
  - Используется для генерации клиентских SDK

### Мониторинг и здоровье системы

- **Health Check**: `http://localhost:8000/health/check-db` - проверка подключения к БД
- **Prometheus метрики**: `http://localhost:8000/metrics` - метрики производительности приложения
- **Панель администратора**: `http://localhost:8000/admin` - управление данными через SQLAdmin

### Особенности документации

1. **Автоматическое обновление**: Документация всегда актуальна и синхронизирована с кодом
2. **Валидация схем**: Все Pydantic-схемы автоматически включаются в документацию
3. **Примеры запросов**: Для каждого эндпоинта генерируются примеры корректных запросов
4. **Безопасность**: Документация поддерживает OAuth2 и JWT аутентификацию

> **Примечание**: В production окружении рекомендуется ограничить доступ к `/docs` и `/redoc` или отключить их с помощью параметра `docs_url=None` и `redoc_url=None` в конструкторе FastAPI.

### Основные endpoint'ы

#### Аутентификация
- `POST /api/v1/api/v1/users/register` - регистрация нового пользователя
- `POST /api/v1/api/v1/users/login` - вход и получение JWT токена
- `GET /api/v1/api/v1/users/me` - информация о текущем пользователе

#### Кошельки
- `POST /api/v1/walletss/` - создание нового кошелька
- `GET /api/v1/walletss/` - список кошельков пользователя
- `GET /api/v1/walletss/{wallet_id}` - информация о кошельке
- `PUT /api/v1/walletss/{wallet_id}` - обновление кошелька
- `DELETE /api/v1/walletss/{wallet_id}` - удаление кошелька

#### Операции
- `POST /api/v1/operations/add-money` - пополнение кошелька
- `POST /api/v1/operations/withdraw-money` - снятие средств
- `POST /api/v1/operations/transfer-money` - перевод между кошельками
- `GET /api/v1/operations/history` - история операций с пагинацией и фильтрацией

#### Мониторинг
- `GET /health/check-db` - проверка подключения к БД


### Примеры использования API

#### 1. Регистрация пользователя
```bash
curl -X POST "http://localhost:8000/api/v1/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password123"
  }'
```

#### 2. Вход и получение токена
```bash
curl -X POST "http://localhost:8000/api/v1/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password123"
  }'
```

Ответ:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### 3. Создание кошелька
```bash
curl -X POST "http://localhost:8000/api/v1/walletss/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Основной кошелек",
    "balance": 1000.00,
    "currency": "RUB"
  }'
```

#### 4. Пополнение кошелька
```bash
curl -X POST "http://localhost:8000/api/v1/operations/add-money" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_name": "Основной кошелек",
    "amount": 500.00,
    "description": "Зарплата за апрель"
  }'
```

#### 5. Получение истории операций с пагинацией
```bash
curl -X GET "http://localhost:8000/api/v1/operations/history?offset=0&limit=10&sort_param=created_at&dir=desc" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

#### 6. Проверка здоровья БД
```bash
curl -X GET "http://localhost:8000/health/check-db"
```

Ответ:
```json
{
  "version": "PostgreSQL 17.0 on x86_64-pc-linux-gnu, compiled by gcc (Debian 12.2.0-14) 12.2.0, 64-bit"
}
```

## 🔐 Аутентификация

API использует JWT (JSON Web Tokens) для аутентификации. Для доступа к защищенным endpoint'ам необходимо:

1. Зарегистрироваться через `/api/v1/api/v1/users/register`
2. Войти через `/api/v1/api/v1/users/login` для получения токена
3. Добавить заголовок `Authorization: Bearer <your_token>` к запросам

Пример запроса с токеном:
```bash
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  http://localhost:8000/api/v1/walletss/
```

## 🧪 Тестирование

Проект имеет высокое тестовое покрытие (94%, подтверждено pytest-cov). Для запуска тестов:

```bash
# Запуск всех тестов с покрытием и HTML отчетом
uv run pytest --cov=app --cov-report=html

# Запуск тестов с детальным выводом
uv run pytest -v

# Запуск тестов конкретной категории
uv run pytest tests/test_services/ -v
uv run pytest tests/test_routers/ -v

# Запуск тестов с генерацией отчета о покрытии в терминале
uv run pytest --cov=app --cov-report=term-missing

# Запуск тестов в режиме watch (требуется pytest-watch)
uv run ptw -- --testmon
```

После запуска тестов с HTML отчетом, откройте `htmlcov/index.html` в браузере для визуализации покрытия.

### Структура тестов

- **Unit-тесты**: `tests/test_schemas/`, `tests/test_services/`
- **Интеграционные тесты**: `tests/test_repositories/`, `tests/test_db/`
- **API тесты**: `tests/test_routers/`, `tests/test_handlers.py`
- **Тесты инфраструктуры**: `tests/test_redis.py`

### Запуск тестов в Docker

```bash
# Запуск тестов в контейнере
docker-compose exec app uv run pytest

# Запуск тестов с покрытием в контейнере
docker-compose exec app uv run pytest --cov=app
```

### Конфигурация тестов

Тесты используют отдельное окружение с настройками из `.env-test`. База данных для тестов создается и удаляется автоматически с помощью фикстур в `tests/conftest.py`.

## 🐳 Docker

### Сервисы Docker Compose

1. **finance_tracker_app** - основное приложение (порт 8000)
2. **finance_tracker_db** - PostgreSQL 17 (порт 6432)
3. **finance_tracker_redis** - Redis 7 (порт 6379)
4. **redis_gui** - RedisInsight для мониторинга Redis (порт 5540)

### Сборка образа

```bash
docker build -t finance-tracker:latest .
```

### Запуск в production

Для production использования рекомендуется:
1. Использовать `.env.prod` с production настройками
2. Настроить reverse proxy (nginx)
3. Включить SSL/TLS сертификаты
4. Настроить мониторинг и логирование

## 📊 Миграции базы данных

Проект использует Alembic для управления миграциями:

```bash
# Создание новой миграции
uv run alembic revision --autogenerate -m "Описание изменений"

# Применение миграций
uv run alembic upgrade head

# Откат миграции
uv run alembic downgrade -1

# Просмотр истории миграций
uv run alembic history
```

## ⚙️ Конфигурация

Основные настройки приложения задаются через переменные окружения:

| Переменная | Описание | Пример |
|------------|----------|--------|
| `ENVIRONMENT` | Окружение (DEV/TEST/PROD) | `DEV` |
| `DB_DRIVER` | Драйвер БД | `postgresql+asyncpg` |
| `DB_USER` | Пользователь БД | `postgres` |
| `DB_PASSWORD` | Пароль БД | `password` |
| `DB_HOST` | Хост БД | `localhost` |
| `DB_PORT` | Порт БД | `5432` |
| `DB_NAME` | Имя БД | `finance_tracker` |
| `REDIS_HOST` | Хост Redis | `localhost` |
| `REDIS_PORT` | Порт Redis | `6379` |
| `SECRET_KEY` | Секретный ключ для JWT | `your-secret-key` |
| `ALGORITHM` | Алгоритм JWT | `HS256` |

## 🛠️ Разработка

### Установка для разработки

```bash
# Клонирование репозитория
git clone <repository-url>
cd finance-tracker

# Установка зависимостей
uv sync --dev

# Настройка pre-commit хуков (опционально)
uv run pre-commit install

# Запуск линтера
uv run ruff check .
```

### Структура проекта

```
finance-tracker/
├── app/                    # Исходный код приложения
│   ├── api/               # API слой
│   ├── core/              # Ядро приложения
│   ├── models/            # Модели базы данных
│   ├── repository/        # Репозитории данных
│   ├── services/          # Бизнес-логика
│   ├── schemas/           # Pydantic схемы
│   ├── uow/               # Unit of Work
│   ├── utils/             # Вспомогательные утилиты
│   ├── connectors/        # Коннекторы
│   └── exceptions/        # Исключения
├── tests/                 # Тесты
├── migrations/            # Миграции базы данных
├── docker-compose.yml     # Docker Compose конфигурация
├── Dockerfile            # Docker образ
├── pyproject.toml        # Зависимости и конфигурация
└── README.md             # Документация
```

### Code Style

Проект использует следующие инструменты для поддержания качества кода:

- **Ruff** - линтер и форматтер
- **mypy** - статическая типизация (опционально)
- **pytest** - тестирование
- **pre-commit** - pre-commit хуки

## 📈 Производительность

Приложение оптимизировано для высокой производительности:

1. **Асинхронность** - все операции I/O выполняются асинхронно
2. **Кэширование** - Redis кэш для частых запросов
3. **Индексы БД** - индексы на часто запрашиваемых полях
4. **Connection Pooling** - пул соединений с БД
5. **Лимитирование** - защита от чрезмерной нагрузки

## 🔧 Утилиты

### Проверка здоровья системы

```bash
curl http://localhost:8000/health
```

Ответ:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "database": "connected",
    "redis": "connected"
  }
}
```

### Проверка подключения к БД

```bash
curl http://localhost:8000/handlers/check-db
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для вашей фичи (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
4. Запушьте ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

### Требования к коду

- Все новые функции должны быть покрыты тестами
- Код должен соответствовать стилю проекта (ruff)
- Документация должна быть обновлена при необходимости
- Миграции БД должны быть обратно совместимы

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. Подробнее см. в файле [LICENSE](LICENSE).

## 📞 Контакты и поддержка

- **Issues**: [GitHub Issues](https://github.com/yourusername/finance-tracker/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/finance-tracker/discussions)

## 🙏 Благодарности

- FastAPI сообществу за отличный фреймворк
- SQLAlchemy за мощный ORM
- Всем контрибьюторам проекта

## ❓ Часто задаваемые вопросы (FAQ)

### Q: Как сбросить базу данных к начальному состоянию?
A: Используйте команды Alembic:
```bash
# Откатить все миграции
uv run alembic downgrade base

# Применить миграции заново
uv run alembic upgrade head
```

### Q: Как добавить новую модель в базу данных?
A:
1. Создайте модель в `app/models/`
2. Импортируйте модель в `app/models/__init__.py`
3. Создайте автоматическую миграцию:
```bash
uv run alembic revision --autogenerate -m "add_new_model"
```
4. Примените миграцию:
```bash
uv run alembic upgrade head
```

### Q: Как работает кэширование в приложении?
A: Приложение использует Redis для кэширования. Кэш автоматически инвалидируется при изменении данных. Время жизни кэша настраивается в декораторах `@FastAPICache.decorate()`.

### Q: Как настроить лимитирование запросов?
A: Лимитирование настроено через `fastapi-limiter`. Настройки находятся в `app/api/dependencies.py`. По умолчанию: 10 запросов в секунду на IP.

### Q: Как добавить новый endpoint API?
A:
1. Создайте роутер в `app/api/v1/` или добавьте endpoint в существующий роутер
2. Реализуйте бизнес-логику в соответствующем сервисе
3. Добавьте зависимости и обработку ошибок
4. Напишите тесты для нового endpoint'а

### Q: Как работает аутентификация?
A: Используется JWT (JSON Web Tokens). При успешном входе выдается access token, который нужно передавать в заголовке `Authorization: Bearer <token>`. Токен действителен 30 минут.

### Q: Как настроить приложение для production?
A:
1. Создайте `.env.prod` с production настройками
2. Измените `ENVIRONMENT=PROD`
3. Используйте сильный `SECRET_KEY`
4. Настройте SSL/TLS через reverse proxy (nginx)
5. Включите мониторинг и логирование

## 🐛 Поиск и устранение неисправностей

### Проблема: Не удается подключиться к базе данных
**Решение:**
- Проверьте, что PostgreSQL запущен: `docker-compose ps`
- Проверьте настройки подключения в `.env.dev`
- Проверьте логи: `docker-compose logs postgres`

### Проблема: Redis не отвечает
**Решение:**
- Проверьте, что Redis запущен: `redis-cli ping`
- Проверьте настройки хоста и порта
- Очистите кэш: `redis-cli flushall`

### Проблема: Миграции не применяются
**Решение:**
- Проверьте, что Alembic настроен правильно: `uv run alembic current`
- Убедитесь, что у пользователя БД есть права на создание таблиц
- Проверьте логи Alembic: `uv run alembic upgrade head --sql`

### Проблема: Тесты не проходят
**Решение:**
- Убедитесь, что тестовая БД доступна
- Проверьте наличие `.env-test` файла
- Запустите тесты с флагом `-v` для детального вывода

## 📈 Дальнейшее развитие

Планируемые улучшения:
- [ ] Добавление вебсокетов для real-time уведомлений
- [ ] Интеграция с платежными системами
- [ ] Генерация PDF отчетов
- [ ] Мобильное приложение (React Native)
- [ ] Machine learning для анализа расходов
- [ ] Мультивалютная поддержка
- [ ] API для сторонних разработчиков

## 🤝 Сообщество

Присоединяйтесь к нашему сообществу:
- [GitHub Discussions](https://github.com/yourusername/finance-tracker/discussions) - обсуждение идей и вопросов
- [GitHub Issues](https://github.com/yourusername/finance-tracker/issues) - баг-репорты и feature requests
- [Discord](https://discord.gg/your-invite) - чат для разработчиков

## 🌟 Звезды и поддержка

Если этот проект был полезен для вас, поставьте звезду на GitHub! Это помогает проекту развиваться.

---

**Примечание**: Этот проект находится в активной разработке. API может изменяться между минорными версиями. Перед обновлением проверяйте [CHANGELOG.md](CHANGELOG.md) (если есть).

**Лицензия**: MIT © 2024 Finance Tracker Team