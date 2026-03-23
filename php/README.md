# LVR Music Publishing — PHP (Laravel)

PHP-версия личного кабинета LVR Music Publishing на Laravel 11.

## Требования

- PHP 8.2+
- Composer
- SQLite (для разработки) или MySQL

## Установка

1. Перейдите в папку `php`:
```bash
cd php
```

2. Установите зависимости:
```bash
composer install
```

3. Скопируйте `.env.example` в `.env`:
```bash
copy .env.example .env
```

4. Сгенерируйте ключ приложения:
```bash
php artisan key:generate
```

5. Создайте базу данных SQLite (для разработки):
```bash
# Создайте пустой файл database/database.sqlite
# или укажите путь в .env: DB_DATABASE=путь/к/database.sqlite
```

6. Выполните миграции:
```bash
php artisan migrate
```

7. Скопируйте статические файлы из Python-версии:
```bash
# Windows (PowerShell)
Copy-Item -Path "..\app\static\*" -Destination "public\static\" -Recurse -Force

# Linux/macOS
cp -r ../app/static/* public/static/
```

8. Создайте симлинк для загрузок (если нужны uploads):
```bash
php artisan storage:link
```

9. Создайте тестовые данные (режим разработки):
- Откройте в браузере: http://localhost:8000/dev-setup
- Или установите `APP_DEBUG=true` в `.env` и перейдите по ссылке

## Запуск

```bash
php artisan serve
```

Приложение будет доступно по адресу: http://127.0.0.1:8000

### Тестовые учётные записи (после dev-setup)

- **admin** / Admin123!
- **artist** / Artist123!
- **label** / Label123!

## Структура проекта

```
php/
├── app/
│   ├── Http/Controllers/   # Контроллеры
│   ├── Models/             # Eloquent модели
│   └── Providers/
├── config/                 # Конфигурация
├── database/migrations/    # Миграции БД
├── public/                 # Точка входа, статика
├── resources/views/        # Blade шаблоны
├── routes/web.php         # Маршруты
└── storage/               # Загрузки, кэш, сессии
```

## Реализованные модули

- ✅ Авторизация (логин/пароль, callback по токену)
- ✅ Dashboard (главная)
- ✅ Релизы (CRUD, модерация, экспорт CSV)
- ✅ Модели: User, Release, Track, Platform, Finance, Ticket, Contract, SmartLink и др.

## Production

Для production используйте nginx/Apache с PHP-FPM. Укажите корень документа на папку `public/`.

```bash
# Пример для production
php artisan config:cache
php artisan route:cache
php artisan view:cache
```
