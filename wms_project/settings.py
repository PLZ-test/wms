# wms_project/settings.py
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-##################################################'

DEBUG = True

ALLOWED_HOSTS = ['*', '127.0.0.1', 'localhost', '192.168.2.116', '192.168.2.121', '192.168.2.127', '192.168.2.129']

# Application definition
# [수정] INSTALLED_APPS 목록을 각 앱의 설정 클래스(apps.py) 전체 경로로 명시합니다.
# 이렇게 하면 Django가 앱을 더 명확하게 인식할 수 있습니다.
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
# ---------------------------------------------------

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