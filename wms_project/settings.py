"""
Django settings for wms_project project.
"""

from pathlib import Path
import os

# 📁 Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# 🛡️ Security
SECRET_KEY = 'django-insecure-##################################################'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '192.168.2.116', '192.168.2.121', '192.168.2.127']

# 📦 Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'wms_app.apps.WmsAppConfig',  # ✅ 너의 앱 등록
]

# 🧱 Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wms_app.middleware.FilterPersistenceMiddleware',  # ✅ 사용자 정의 미들웨어
]

# 🌐 URLConf
ROOT_URLCONF = 'wms_project.urls'

# 🧠 Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # ✅ 커스텀 템플릿 경로
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wms_app.context_processors.filters',  # ✅ 커스텀 context processor
            ],
        },
    },
]

# 🌀 WSGI
WSGI_APPLICATION = 'wms_project.wsgi.application'

# 🗄️ Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 🔐 Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 🌍 Localization
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True
USE_L10N = True  # 💡 한국어 날짜 등 포맷 로컬라이징

# 🎨 Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# 🧾 기본 기본키 필드
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 👤 사용자 정의 모델
AUTH_USER_MODEL = 'wms_app.User'

# 🔐 로그인/로그아웃 설정
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
