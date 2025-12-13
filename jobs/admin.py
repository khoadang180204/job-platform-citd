from django.contrib import admin
from .models import Company, Skill, Job, Application

admin.site.register(Company)
admin.site.register(Application)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'job_type', 'location', 'created_at']
    search_fields = ['title', 'company__name']
    list_filter = ['job_type', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['required_skills']  # Để chọn skills dễ dàng