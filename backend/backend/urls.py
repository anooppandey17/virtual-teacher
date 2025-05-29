# backend/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # dj-rest-auth endpoints
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),

    # (Optional) email confirmation via allauth
    path('api/auth/', include('allauth.urls')),  

    path('api/users/', include('users.urls')),

     path('api/learners/', include('learners.urls')),
    path('api/teachers/', include('teachers.urls')),
    path('api/parents/',  include('parents.urls')),



]
