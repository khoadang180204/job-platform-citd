from django.db import models
from django.conf import settings

class Company(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name

class Job(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    skills = models.ManyToManyField(Skill, blank=True)
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    resume_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = (('pending','Pending'), ('accepted','Accepted'), ('rejected','Rejected'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
