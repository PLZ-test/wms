"""
Django settings for wms_project project.
"""

from pathlib import Path
import os # 이 줄이 없으면 아래 os.path.join에서 오류가 납니다.

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-##################################################' # 이 부분은 원래 있던 그대로 두세요.

DEBUG = True

ALLOWED_HOSTS = ['192.168.2.116']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'wms_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wms_app.middleware.FilterPersistenceMiddleware', # 이 미들웨어가 누락되었을 수 있습니다. 추가해주세요.
]

ROOT_URLCONF = 'wms_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wms_app.context_processors.filters', # 이 컨텍스트 프로세서가 누락되었을 수 있습니다. 추가해주세요.
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
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True


# --- Static files (CSS, JavaScript, Images) ---
# 이 부분이 가장 중요합니다!

# 웹 페이지에서 정적 파일을 부를 때 사용할 URL (예: /static/css/style.css)
STATIC_URL = 'static/'

# 개발 환경에서 장고가 정적 파일을 추가로 검색할 경로 목록
# 프로젝트 최상위 폴더에 있는 'static' 폴더를 가리키도록 설정합니다.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'