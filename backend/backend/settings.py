# import dj_database_url
from decouple import config
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "dj_rest_auth",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "dj_rest_auth.registration",
    'django.contrib.sites',
    "allauth.socialaccount.providers.google",
    "users",
    "learners",
    "chat",
    "ai",
    "teachers",
    "parents",
    "prompts"
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
}

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('Bearer',),
    # you can customize token lifetime here if you like
}

SITE_ID = 1

TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
TOGETHER_API_KEY = config('TOGETHER_API_KEY')  # Read from .env file
TOGETHER_MODEL = config('TOGETHER_MODEL', default="mistralai/Mixtral-8x7B-Instruct-v0.1")  # Or your preferred model


REST_AUTH = {
    'REGISTER_SERIALIZER': 'users.serializers.CustomRegisterSerializer',
}

# Allauth configuration
# ACCOUNT_EMAIL_VERIFICATION = 'mandatory'     # require email verification
ACCOUNT_EMAIL_VERIFICATION = 'none'            # for testing purposes
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1
ACCOUNT_UNIQUE_EMAIL = True

SITE_ID = 1
# which fields users can use to log in
ACCOUNT_LOGIN_METHODS = ['email', 'username']

# which fields are collected at signup
ACCOUNT_SIGNUP_FIELDS = {
    'username*',
    'email*',
    'password1*',
    'password2*',
    'first_name*',
    'last_name*',
    'role*',
    'gender*',
    'phone_number*',
}

ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',            # for username/password
    'allauth.account.auth_backends.AuthenticationBackend',  # for email & social
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"

# CORS settings
CORS_ALLOW_CREDENTIALS = True

# Get frontend URL from environment variable, default to localhost for development
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')

CORS_ALLOWED_ORIGINS = [
    FRONTEND_URL,  # Dynamic frontend URL
]

# Add additional origins if needed (comma-separated in environment variable)
ADDITIONAL_CORS_ORIGINS = config('ADDITIONAL_CORS_ORIGINS', default='').split(',')
if ADDITIONAL_CORS_ORIGINS and ADDITIONAL_CORS_ORIGINS[0]:  # Only add if not empty
    CORS_ALLOWED_ORIGINS.extend([origin.strip() for origin in ADDITIONAL_CORS_ORIGINS if origin.strip()])

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    FRONTEND_URL,  # Dynamic frontend URL
]

# Add additional CSRF origins if needed
if ADDITIONAL_CORS_ORIGINS and ADDITIONAL_CORS_ORIGINS[0]:
    CSRF_TRUSTED_ORIGINS.extend([origin.strip() for origin in ADDITIONAL_CORS_ORIGINS if origin.strip()])

CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = False  # False since we need to access it in JS
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = True

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     'default': dj_database_url.config(default=config('DATABASE_URL'))
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('PGDATABASE', 'virtual_teacher'),
        'USER': os.getenv('PGUSER', 'vteacher_user'),
        'PASSWORD': os.getenv('PGPASSWORD', 'password'),
        'HOST': os.getenv('PGHOST', 'localhost'),
        'PORT': os.getenv('PGPORT', '5432'),
    }
}



# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = 'users.User'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
