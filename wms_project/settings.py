# wms_project/settings.py
from pathlib import Path
import os

# 📁 Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# 🛡️ Security
SECRET_KEY = 'django-insecure-##################################################'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '192.168.2.116', '192.168.2.121', '192.168.2.127']

<<<<<<< HEAD
ALLOWED_HOSTS = ['*','192.168.2.129']

# Application definition
# --- [수정] INSTALLED_APPS 목록의 순서를 변경 ---
# 우리가 만든 앱들을 Django 기본 앱들보다 먼저 오도록 수정합니다.
=======
# 📦 Installed apps
>>>>>>> 231c207effbc0089f2b998d2ac5639725c746dfc
INSTALLED_APPS = [
    # Custom Apps
    'core',
    'users',
    'management',
    'stock',
    'orders',
    'settlement',
    
    # Django Default Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
<<<<<<< HEAD
=======
    'wms_app.apps.WmsAppConfig',  # ✅ 너의 앱 등록
>>>>>>> 231c207effbc0089f2b998d2ac5639725c746dfc
]
# ---------------------------------------------------

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
<<<<<<< HEAD
    'core.middleware.FilterPersistenceMiddleware',
=======
    'wms_app.middleware.FilterPersistenceMiddleware',  # ✅ 사용자 정의 미들웨어
>>>>>>> 231c207effbc0089f2b998d2ac5639725c746dfc
]

# 🌐 URLConf
ROOT_URLCONF = 'wms_project.urls'

<<<<<<< HEAD
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
=======
# 🧠 Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # ✅ 커스텀 템플릿 경로
>>>>>>> 231c207effbc0089f2b998d2ac5639725c746dfc
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
<<<<<<< HEAD
                'core.context_processors.filters',
=======
                'wms_app.context_processors.filters',  # ✅ 커스텀 context processor
>>>>>>> 231c207effbc0089f2b998d2ac5639725c746dfc
            ],
        },
    },
]

# 🌀 WSGI
WSGI_APPLICATION = 'wms_project.wsgi.application'

<<<<<<< HEAD
# Database
=======
# 🗄️ Database
>>>>>>> 231c207effbc0089f2b998d2ac5639725c746dfc
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

<<<<<<< HEAD
# Password validation
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
=======
# 🔐 Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 🌍 Localization
>>>>>>> 231c207effbc0089f2b998d2ac5639725c746dfc
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True
USE_L10N = True  # 💡 한국어 날짜 등 포맷 로컬라이징

<<<<<<< HEAD
# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
=======
# 🎨 Static files
STATIC_URL = '/static/'
>>>>>>> 231c207effbc0089f2b998d2ac5639725c746dfc
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

<<<<<<< HEAD
# Custom User Model 설정
AUTH_USER_MODEL = 'users.User'

# 로그인/로그아웃 URL 설정
LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'core:dashboard'
=======
# 🧾 기본 기본키 필드
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 👤 사용자 정의 모델
AUTH_USER_MODEL = 'wms_app.User'

# 🔐 로그인/로그아웃 설정
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
>>>>>>> 231c207effbc0089f2b998d2ac5639725c746dfc
