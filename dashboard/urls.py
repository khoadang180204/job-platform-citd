from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Overview
    path('', views.dashboard_index, name='index'),
    
    # Job Management
    path('jobs/', views.manage_jobs, name='manage_jobs'),
    path('jobs/create/', views.create_job, name='create_job'),
    path('jobs/<int:pk>/edit/', views.edit_job, name='edit_job'),
    path('jobs/<int:pk>/delete/', views.delete_job, name='delete_job'),
    path('jobs/<int:pk>/applications/', views.job_applications, name='job_applications'),
    
    # Applications
    path('applications/', views.all_applications, name='all_applications'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
    path('applications/<int:app_id>/update-status/', views.update_application_status, name='update_application_status'),
    
    # Settings
    path('company/', views.company_settings, name='company_settings'),
]