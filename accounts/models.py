from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('candidate','Candidate'),
        ('employer','Employer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='candidate')

    def is_candidate(self):
        return self.role == 'candidate'

    def is_employer(self):
        return self.role == 'employer'
