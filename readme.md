Небольшое Flask-приложение для загрузки JSON-файлов и хранения их содержимого в PostgreSQL. 
В продакшене разворачивается за Nginx + Gunicorn + systemd.

---

## Оглавление

- Описание проекта
- Требования
- Установка и первоначальная настройка
- Настройка базы данных и миграции
- Запуск Gunicorn через systemd
- Настройка Nginx
- Запуск и проверка
- Обновление приложения

---

## Описание проекта

Это простое веб-приложение на Flask. Пользователь может загружать JSON-файл с записями, а сервер сохраняет данные в базу PostgreSQL и отображает их на странице.

---

## Требования

- Ubuntu 24.04+
- Python 3.12  
- PostgreSQL 11+  
- Nginx 1.18+  
- systemd  

---

## Установка и первоначальная настройка

1. Клонируйте репозиторий и перейдите в папку проекта:  
   ```bash
   git clone https://github.com/AndreiParmon/flsk_0708.git
   cd flsk_0708

2. Создайте виртуальное окружение и активируйте его:
    ```bash
	python3 -m venv .venv
	source .venv/bin/activate
	
3. Установите зависимости:
	pip install --upgrade pip
	pip install -r requirements.txt
	
4. Отредактируйте файл config.py в корне проекта и задайте все параметры:
	SQLALCHEMY_DATABASE_URI = "postgresql://<пользователь БД>:<пароль от БД>@localhost:5432/<название БД>"
	#SQLALCHEMY_DATABASE_URI = "postgresql://test:pass@localhost:5432/testdb"
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
	UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')


5. Задайте владельца папки для загрузок файлов:
	sudo chown -R $USER:$USER <путь до проекта>/uploads
	#sudo chown -R $Andrei:$Andrei /home/andrei/flsk_0708/uploads


## Настройка базы данных и миграции

1. Войдите в PostgreSQL и создайте пользователя и базу данных:
	CREATE USER <name user> WITH PASSWORD 'password';
	CREATE DATABASE <name BD> OWNER <name user>;
	
2. Инициализируйте миграции (один раз):
	flask db init
3. Создайте миграцию и примените её:
	flask db migrate -m "Initial migration"
	flask db upgrade

---

## Запуск Gunicorn через systemd

Создайте файл /etc/systemd/system/flsk_0708.service:
	[Unit]
	Description=Gunicorn for Flask JSON App flsk_0708
	After=network.target

	[Service]
	User=andrei # пользователь
	Group=andrei # пользователь
	WorkingDirectory=/home/andrei/flsk_0708
	Environment="PATH=/home/andrei/flsk_0708/.venv/bin"
	ExecStart=/home/andrei/flsk_0708/.venv/bin/gunicorn \
	  --workers 3 \
	  --bind unix:/home/andrei/flsk_0708/flsk_0708.sock \
	  run:app
	Restart=always

	[Install]
	WantedBy=multi-user.target


После сохранения выполните:
	sudo systemctl daemon-reload
	sudo systemctl enable flsk_0708
	sudo systemctl start flsk_0708
	sudo systemctl status flsk_0708

---

## Настройка Nginx

1. Создайте файл /etc/nginx/sites-available/flsk_0708:
	upstream flask_app {
		server 127.0.0.1:8000;
	}

	server {
		listen 80 default_server;
		listen [::]:80 default_server;
		server_name _; 

		# общие заголовки
		client_max_body_size 10M;
		sendfile on;

		location /static/ {
			alias /home/andrei/flsk_0708/app/static/;
		}

		location / {
			proxy_set_header Host              $host;
			proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
			proxy_set_header X-Real-IP         $remote_addr;
			proxy_pass http://flask_app;
		}
	}

2. Активируйте сайт и перезагрузите Nginx:
	sudo ln -s /etc/nginx/sites-available/flsk_0708 /etc/nginx/sites-enabled/
	sudo nginx -t
	sudo systemctl reload nginx

---

Запуск и проверка
- Откройте в браузере http://localhost/ (или http://127.0.0.1:8000/).
- Перейдите на http://localhost/upload и загрузите валидный JSON-файл.
- Перейдите на главную страницу — должна появиться загруженная запись.
