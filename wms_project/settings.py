# wms_project/settings.py
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-##################################################'

DEBUG = True

ALLOWED_HOSTS = ['*', '127.0.0.1', 'localhost', '192.168.2.116', '192.168.2.121', '192.168.2.127', '192.168.2.129']

# Application definition
INSTALLED_APPS = [
    # Custom Apps
    'core.apps.CoreConfig',
    'users.apps.UsersConfig',
    'management.apps.ManagementConfig',
    'stock.apps.StockConfig',
    'orders.apps.OrdersConfig',
    'settlement.apps.SettlementConfig',

    # Django Default Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.FilterPersistenceMiddleware',
]

ROOT_URLCONF = 'wms_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.filters',
            ],
        },
    },
]

WSGI_APPLICATION = 'wms_project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Custom User Model 설정
AUTH_USER_MODEL = 'users.User'

# 로그인/로그아웃 URL 설정
LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'core:dashboard'
LOGOUT_REDIRECT_URL = 'users:login'

# 캐시 설정
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# --- [신규] 미디어 파일(사용자 업로드 파일) 설정 ---
# 사용자가 업로드한 파일(예: 도면 이미지)에 웹에서 접근할 때 사용할 URL 경로
MEDIA_URL = '/media/'

# 사용자가 업로드한 파일을 실제 서버 컴퓨터의 어느 폴더에 저장할지 경로를 지정
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')