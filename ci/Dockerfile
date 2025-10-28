FROM python:3.13-slim-bookworm

WORKDIR /app

# Установка служебных пакетов
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    postgresql-client \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Создание и активация виртуального окружения
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Установка зависимостей проекта
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем ВСЕ файлы проекта
COPY . .

# Настройка проекта перед стартом
ENTRYPOINT ["./prestart.sh"]
