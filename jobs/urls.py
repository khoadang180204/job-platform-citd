from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='list'),
    path('<int:pk>/', views.job_detail, name='detail'),
    path('<int:pk>/apply/', views.apply_job, name='apply'),
    path('create/', views.create_job, name='create'),
    path('<int:pk>/edit/', views.edit_job, name='edit'),
    path('<int:pk>/delete/', views.delete_job, name='delete'),
]