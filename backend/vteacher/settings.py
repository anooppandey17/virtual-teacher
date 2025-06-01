# Add to the end of the file

# Media files (Uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Update INSTALLED_APPS to include django-cleanup
INSTALLED_APPS += [
    'django_cleanup.apps.CleanupConfig',  # Automatically delete old files
] 