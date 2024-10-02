"""
Django settings for test project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

# DEBUG mode should be set to False in production
DEBUG = True  # This should raise a security issue

# SECRET_KEY should not be hardcoded; use an environment variable instead
SECRET_KEY = 'supersecretkey'  # This should raise a security issue

# ALLOWED_HOSTS should not be empty and should avoid wildcards in production
ALLOWED_HOSTS = ['*']  # This should raise a security issue

# CSRF_COOKIE_SECURE should be set to True in production
CSRF_COOKIE_SECURE = False  # This should raise a security issue

# SESSION_COOKIE_SECURE should be set to True in production
SESSION_COOKIE_SECURE = False  # This should raise a security issue

# SECURE_SSL_REDIRECT should be enabled in production
SECURE_SSL_REDIRECT = False  # This should raise a security issue

# X_FRAME_OPTIONS should be either 'DENY' or 'SAMEORIGIN' to prevent clickjacking
X_FRAME_OPTIONS = 'SAMEORIGIN'  # This should pass

# SECURE_HSTS_SECONDS should be set to a positive value in production to enforce HTTPS
SECURE_HSTS_SECONDS = 0  # This should raise a security issue

# SECURE_HSTS_INCLUDE_SUBDOMAINS should be set to True if SECURE_HSTS_SECONDS is positive
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # This should raise an issue since SECURE_HSTS_SECONDS is 0

# Middleware settings
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',  # This should raise an issue for missing middleware
]