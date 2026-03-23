# Личный кабинет LVR Music Publishing

Веб-приложение для управления музыкальными релизами, аналитикой и финансами лейбла (luisv-records.ru).

## Стек

- **Backend:** Python 3.10+, Flask 3.x
- **ORM:** SQLAlchemy (Flask-SQLAlchemy)
- **База данных:** SQLite (dev) / PostgreSQL (prod)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Шаблоны:** Jinja2

## Установка

1. Клонируйте репозиторий и перейдите в каталог проекта.

2. Создайте виртуальное окружение:
```bash
python -m venv venv
venv\Scripts\activate   # Windows
# или: source venv/bin/activate  # Linux/macOS
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Скопируйте `.env.example` в `.env` и при необходимости отредактируйте:
```bash
copy .env.example .env   # Windows
# или: cp .env.example .env  # Linux/macOS
```

5. Запуск в режиме разработки:
```bash
python run.py
```
Приложение будет доступно по адресу: http://127.0.0.1:5000

### Режим разработки (без внешнего auth)

В режиме разработки (`FLASK_DEBUG=1`) доступны:

- **Вход для разработки:** http://127.0.0.1:5000/dev-login  
- **Создание тестовых данных:** http://127.0.0.1:5000/dev-setup  

После выполнения `/dev-setup` создаются пользователи:
- **admin** / Admin123!
- **artist** / Artist123!
- **label** / Label123!

И список платформ распространения по умолчанию.

**Обновить email администратора** (если в БД остался старый адрес и коды подтверждения приходят не на ту почту):
- В режиме отладки: откройте **https://ваш-домен/dev-update-admin-email** (или с `FLASK_DEBUG=1` локально).
- На продакшене: задайте в окружении `ALLOW_UPDATE_ADMIN_EMAIL=1`, один раз откройте `/dev-update-admin-email`, затем уберите переменную.
- Email администратора будет установлен в `press.saidman@gmail.com`.

## Production

```bash
gunicorn -w 4 -b 127.0.0.1:8000 "wsgi:app"
```

Перед запуском задайте в `.env`:
- `FLASK_ENV=production`
- `SECRET_KEY` — надёжный секретный ключ
- `DATABASE_URL` — строка подключения к БД (для PostgreSQL)

## Структура проекта

```
LKSYSTEM/
├── app/
│   ├── __init__.py       # фабрика приложения
│   ├── config.py         # конфигурация
│   ├── models/           # модели SQLAlchemy
│   ├── routes/           # Blueprint'ы (роуты)
│   ├── templates/        # Jinja2 шаблоны
│   ├── static/           # CSS, JS, изображения
│   └── utils/            # хелперы, валидация
├── uploads/              # загруженные файлы
├── instance/             # SQLite БД (dev)
├── .env.example
├── requirements.txt
├── run.py                # dev-сервер
├── wsgi.py               # точка входа для Gunicorn
└── README.md
```

## Основные разделы

- **Релизы** — создание, редактирование, отправка на модерацию, экспорт каталога
- **Модерация** — одобрение/отклонение релизов (админ)
- **Финансы** — отчёты по кварталам, согласование выплат
- **Смарт-ссылки** — создание и статистика
- **Новости** — просмотр и управление (админ)
- **Тикеты** — поддержка
- **Договоры** — просмотр и подписание
- **Пользователи / Лейблы / Платформы** — администрирование

## Документация

Полное техническое задание: `Тех.Задание/TECHNICAL_SPECIFICATION.md`

## Лицензия

Проект защищён авторским правом. Использование и копирование без разрешения запрещены.  
Подробности на русском и английском — в файле [LICENSE](LICENSE).  
Контакты для запроса разрешения: **support@lvr-music-publishing.ru**, **help@vmestesn.ru**.
