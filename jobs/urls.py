from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='list'),
    path('<int:pk>/', views.job_detail, name='detail'),
    path('<int:pk>/apply/', views.apply_job, name='apply'),
    path('<int:pk>/save/', views.save_job, name='save'),
    path('api/districts/<str:province_code>/', views.get_districts, name='api_districts'),
    path('api/wards/<str:district_code>/', views.get_wards, name='api_wards'),
    path('api/skills/<int:category_id>/', views.get_skills_by_category, name='api_skills'),
]