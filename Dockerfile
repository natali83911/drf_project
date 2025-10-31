# Базовый образ Python (оптимальный)
FROM python:3.12-slim

# Обновляем пакеты и ставим системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libtiff-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    libpng-dev \
    locales \
    && rm -rf /var/lib/apt/lists/*

# Настройка рабочей директории
WORKDIR /app

# Копируем зависимости проекта (requirements.txt)
COPY requirements.txt /app/

# Устанавливаем зависимости Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем всё приложение внутрь контейнера
COPY . /app/

# Настройки для корректной работы Python в контейнере
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Открываем порт Django
EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]

