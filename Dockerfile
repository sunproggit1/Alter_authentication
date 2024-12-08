
# Базовый образ
FROM python:latest

ENV PYTHONUNBUFFERED 1
# Установка рабочей директории в контейнере
WORKDIR /alter_authentication

# Установка nano и обновление pip
RUN apt-get update && apt-get install -y nano && \
    pip install --upgrade pip && pip install --upgrade pip setuptools

# Установка dos2unix и других необходимых пакетов
RUN apt-get update && \
    apt-get install -y --no-install-recommends dos2unix

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Копирование проекта в контейнер
COPY . .

# Копирование скрипта entrypoint и конвертация его в Unix формат
RUN dos2unix /alter_authentication/entrypoint.sh && \
    chmod +x /alter_authentication/entrypoint.sh

# Открытие порта 8000
EXPOSE 8000

# Команда для выполнения скрипта entrypoint
ENTRYPOINT ["/alter_authentication/entrypoint.sh"]

