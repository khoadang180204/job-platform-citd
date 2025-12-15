from django.contrib import admin
from .models import (
    City, Skill, JobCategory, JobPosition, 
    Requirement, Company, Job, Application, SavedJob
)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['city', 'province', 'population', 'created_at']
    search_fields = ['city', 'province']
    ordering = ['city']

@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_at']
    search_fields = ['name', 'category__name']
    list_filter = ['category']
    ordering = ['name']

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_at']
    search_fields = ['name', 'category']
    list_filter = ['category']
    ordering = ['name']

@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ['requirement_type', 'name', 'created_at']
    search_fields = ['name', 'requirement_type']
    list_filter = ['requirement_type']
    ordering = ['requirement_type', 'name']

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'created_at']
    search_fields = ['name']

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'category', 'job_type', 'city', 'is_active', 'created_at']
    search_fields = ['title', 'company__name', 'category__name']
    list_filter = ['job_type', 'is_active', 'created_at', 'city', 'category']
    filter_horizontal = ['required_skills']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'job', 'status', 'created_at']
    search_fields = ['user__username', 'job__title']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ['user', 'job', 'created_at']
    search_fields = ['user__username', 'job__title']
    list_filter = ['created_at']
    readonly_fields = ['created_at']