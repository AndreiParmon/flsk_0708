Оглавление
- Описание проекта
- Требования
- Установка и первоначальная настройка
- Настройка базы данных и миграции
- Запуск Gunicorn через systemd
- Настройка Nginx
- Запуск и проверка
- Обновление приложения

Описание проекта
Это простое Flask-приложение, позволяющее загружать JSON-файлы с записями и сохранять их в PostgreSQL. 
В продакшене приложение разворачивается за Nginx + Gunicorn.

Требования
- Ubuntu 24.04+ или аналогичный Linux-сервер
- Python 3.12
- PostgreSQL 11+
- Nginx 1.18+
- systemd

Установка и первоначальная настройка
- Клонируйте репозиторий и перейдите в папку:
    git clone 
    cd flask_json_app
- Создайте виртуальное окружение и активируйте его:
    python3 -m venv .venv
    source .venv/bin/activate
- Установите зависимости:
    pip install --upgrade pip
    pip install -r requirements.txt
- Переменные окружения(создайте файл .env в корне проекта или задайте переменные вручную):
    export FLASK_APP=run.py
    export FLASK_ENV=production 
    export DATABASE_URL=postgresql://user:password@localhost:5432/flask_json_app
    export SECRET_KEY="ваш_секретный_ключ"
    export UPLOAD_FOLDER=/var/www/flask_json_app/uploads
- Создайте папку для загрузок и задайте права:
    sudo mkdir -p /var/www/flask_json_app/uploads
    sudo chown -R $USER:$USER /var/www/flask_json_app/uploads
    
Настройка базы данных и миграции
- Подключитесь к PostgreSQL и создайте БД и пользователя:
    CREATE USER flask_user WITH PASSWORD 'password';
    CREATE DATABASE flask_json_app OWNER flask_user;
- Инициализируйте миграции (если ещё не сделано):
    flask db init        # первый запуск – один раз
    flask db migrate -m "Initial migration"
- Примените миграции:
    flask db upgrade

Запуск Gunicorn через systemd
- Создайте файл сервиса /etc/systemd/system/flask_json_app.service:
    [Unit]
    Description=Gunicorn for Flask JSON App
    After=network.target

    [Service]
    User=www-data
    Group=www-data
    WorkingDirectory=/var/www/flask_json_app
    Environment="PATH=/var/www/flask_json_app/.venv/bin"
    Environment="FLASK_ENV=production"
    Environment="DATABASE_URL=postgresql://user:password@localhost:5432/flask_json_app"
    ExecStart=/var/www/flask_json_app/.venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/run/flask_json_app.sock \
          run:app

    [Install]
    WantedBy=multi-user.target
- Перезагрузите systemd и запустите сервис:
    sudo systemctl daemon-reload
    sudo systemctl enable flask_json_app
    sudo systemctl start flask_json_app
    sudo systemctl status flask_json_app

Настройка Nginx
- Создайте конфиг сайта /etc/nginx/sites-available/flask_json_app:
    upstream flask_json_app {
        server unix:/run/flask_json_app.sock fail_timeout=0;
    }
    
    server {
        listen 80;
        server_name example.com;   # замените на ваш домен или IP
    
        root /var/www/flask_json_app;
        index index.html;
    
        location /static/ {
            alias /var/www/flask_json_app/static/;
        }
    
        location / {
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_pass http://flask_json_app;
        }
    }
- Активируйте сайт и проверьте конфигурацию:
    sudo ln -s /etc/nginx/sites-available/flask_json_app /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl reload nginx


Запуск и проверка
- Откройте в браузере http://example.com/ (или IP-сервера).
- Зайдите на http://example.com/upload и загрузите валидный JSON (см. пример в README).
- Проверьте таблицу / – должна отобразиться загруженная запись.

Обновление приложения
- Получите свежие изменения из Git:
    cd /var/www/flask_json_app
    git pull origin main
- Обновите зависимости:
    .venv/bin/pip install -r requirements.txt
- Примените миграции:
    flask db upgrade
- Перезапустите сервисы:
    sudo systemctl restart flask_json_app
    sudo systemctl reload nginx
