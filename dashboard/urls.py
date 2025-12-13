from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index, name='index'),
    path('applications/<int:pk>/', views.job_applications, name='applications'),
    path('update-application/<int:app_id>/', views.update_application_status, name='update_application'),
]