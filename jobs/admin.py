from django.contrib import admin
from .models import (
    Province, District, Ward, Skill, JobCategory, JobPosition, 
    Requirement, Company, Job, Application, SavedJob, UserSkillProfile
)

# Quản lý tỉnh/thành phố
@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'name_with_type', 'type', 'created_at']
    search_fields = ['name', 'name_with_type', 'code']
    list_filter = ['type']
    ordering = ['name']

# Quản lý quận/huyện
@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'name_with_type', 'parent_code', 'type', 'created_at']
    search_fields = ['name', 'name_with_type', 'code']
    list_filter = ['type', 'parent_code']
    ordering = ['name']

# Quản lý phường/xã
@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'name_with_type', 'parent_code', 'type', 'created_at']
    search_fields = ['name', 'name_with_type', 'code']
    list_filter = ['type']
    ordering = ['name']

# Quản lý ngành nghề
@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']

# Quản lý vị trí công việc
@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_at']
    search_fields = ['name', 'category__name']
    list_filter = ['category']
    ordering = ['name']

# Quản lý kỹ năng
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_at']
    search_fields = ['name', 'category']
    list_filter = ['category']
    ordering = ['name']

# Quản lý yêu cầu công việc
@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ['requirement_type', 'name', 'created_at']
    search_fields = ['name', 'requirement_type']
    list_filter = ['requirement_type']
    ordering = ['requirement_type', 'name']

# Quản lý doanh nghiệp
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'created_at']
    search_fields = ['name']

# Quản lý việc làm
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'category', 'job_type', 'province', 'district', 'is_active', 'created_at']
    search_fields = ['title', 'company__name', 'category__name']
    list_filter = ['job_type', 'is_active', 'created_at', 'province', 'category']
    filter_horizontal = ['required_skills']
    readonly_fields = ['created_at', 'updated_at']

# Quản lý ứng tuyển
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'job', 'status', 'created_at']
    search_fields = ['user__username', 'job__title']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

# Quản lý việc đã lưu
@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ['user', 'job', 'created_at']
    search_fields = ['user__username', 'job__title']
    list_filter = ['created_at']
    readonly_fields = ['created_at']

# Quản lý hồ sơ kỹ năng
@admin.register(UserSkillProfile)
class UserSkillProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    list_filter = ['created_at']
    filter_horizontal = ['categories', 'skills']
    readonly_fields = ['created_at', 'updated_at']