import os
from pathlib import Path
from dotenv import load_dotenv  # Импортируем библиотеку для работы с .env файлами



# Загрузка переменных из .env файла
# Теперь все секретные данные хранятся в отдельном файле, а не в коде
load_dotenv()

# Пути внутри проекта собираются так: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ВНИМАНИЕ БЕЗОПАСНОСТИ: храните секретный ключ в секрете в продакшене!
# Берем секретный ключ из переменных окружения, а не из кода
SECRET_KEY = os.getenv('SECRET_KEY')

# ВНИМАНИЕ БЕЗОПАСНОСТИ: не запускайте с DEBUG = True в продакшене!
# Преобразуем строку 'True' в булево значение True
DEBUG = os.getenv('DEBUG') == 'True'

# Берем список разрешенных хостов из .env файла и разбиваем по запятым
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')


# Определение установленных приложений
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app_main',
    'app_next',
]

# Промежуточное программное обеспечение (middleware)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Корневая конфигурация URL
ROOT_URLCONF = 'settings.urls'

# Настройки шаблонов
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI приложение
WSGI_APPLICATION = 'settings.wsgi.application'


# База данных (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'postgres'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}


# Валидация паролей
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Язык и временная зона
LANGUAGE_CODE = 'en-us'  # Код языка (можно поменять на 'ru-ru')
TIME_ZONE = 'UTC'        # Временная зона

USE_I18N = True  # Включение интернационализации
USE_TZ = True    # Использование временных зон


# Статические файлы (CSS, JavaScript, Images)
STATIC_URL = 'static/'


# Автоматическое поле по умолчанию для первичных ключей
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
