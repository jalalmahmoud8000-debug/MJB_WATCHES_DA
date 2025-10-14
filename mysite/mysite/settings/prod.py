from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Add your production domain(s) here
# ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['example.com'])

# Whitenoise for serving static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Use S3 for media files in production
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
