# scripts/seed_jobs.py
import os
import sys
import json

# --- ensure project root is on sys.path ---
# file is scripts/seed_jobs.py, project root is parent dir of scripts/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# --- set DJANGO_SETTINGS_MODULE to your project settings ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobsite.settings')

import django
django.setup()

# ---- Now import models and seed ----
from jobs.models import Company, Job, Skill

def seed():
    script_path = os.path.join(BASE_DIR, 'scripts', 'sample_jobs.json')
    with open(script_path, encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        company_name = item.get('company') or 'Unknown'
        company, _ = Company.objects.get_or_create(name=company_name)
        job = Job.objects.create(
            company=company,
            title=item.get('title','No title'),
            description=item.get('description',''),
            location=item.get('location',''),
        )
        for s in item.get('skills', []):
            skill, _ = Skill.objects.get_or_create(name=s)
            job.skills.add(skill)
        print('Created job:', job.title)

if __name__ == '__main__':
    seed()
