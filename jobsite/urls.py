from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # we'll create minimal urls
    path('jobs/', include('jobs.urls')),
    path('', include('jobs.urls')),  # route root to jobs list
]
