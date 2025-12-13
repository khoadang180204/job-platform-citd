from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('saved-jobs/', views.saved_jobs_view, name='saved_jobs'),
    path('my-applications/', views.my_applications_view, name='my_applications'),
]