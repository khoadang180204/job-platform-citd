from django.contrib import admin
from .models import Company, Skill, Job, Application

admin.site.register(Company)
admin.site.register(Skill)
admin.site.register(Job)
admin.site.register(Application)