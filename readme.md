# Django Two-Factor Authentication System

## Описание проекта
Этот проект представляет собой систему двухфакторной аутентификации с поддержкой дополнительных методов (OTP, Quiz, графический тест).

---

## Требования
1. Установленный [Docker](https://www.docker.com/) (версия >= 20.10).
2. Установленный [Docker Compose](https://docs.docker.com/compose/) (версия >= 2.16).

---

## Установка и запуск
1. Склонируйте репозиторий:
   ```bash
   git clone <URL репозитория>
   cd <название директории>
2. Создайте файл .env в корневой папке проекта и добавьте следующие переменные:
DB_NAME='имя базы данных'
DB_USER='имя пользователя'
DB_PASS='пароль пользователя'

SECRET_KEY=''
DEBUG=TRUE
DJANGO_ALLOWED_HOSTS=localhost,localhost:8082,db_alter_auth
DB_NAME='admin'
DB_USER='admin'
DB_PASS='admin'
DB_HOST='db_alter_auth'
DB_PORT='5432'

EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST='smtp.gmail.com'
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER='' # Вставьте почту с которой можно пускать рассылки
EMAIL_HOST_PASSWORD=''  # Вставьте сгенерированный пароль почты рассылки
DEFAULT_FROM_EMAIL='' # Вставьте почту с которой можно пускать рассылки

3. Запустите Docker Compose:
docker compose up --build -d

4. Откройте браузер и перейдите по адресу: http://localhost:8082.

Что будет сделано
Создание базы данных с настройками.
Инициализация суперпользователя.
Запуск сервера Django через Docker.
Nginx будет проксировать запросы на Django-приложение.
