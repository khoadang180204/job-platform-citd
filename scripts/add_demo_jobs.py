import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobsite.settings')
django.setup()

from jobs.models import Company, Job, Skill

# Tạo Companies
company1 = Company.objects.get_or_create(
    name="TechFlow Solutions",
    defaults={
        "description": "Leading innovation in fintech software",
        "website": "https://techflow.com"
    }
)[0]

company2 = Company.objects.get_or_create(
    name="CloudNine Tech",
    defaults={
        "description": "Cloud infrastructure and SaaS solutions",
        "website": "https://cloudnine.com"
    }
)[0]

# Tạo Skills
skills_data = ["Python", "Django", "PostgreSQL", "AWS", "React", "JavaScript", "Docker", "Kubernetes"]
skills = {}
for skill_name in skills_data:
    skill, _ = Skill.objects.get_or_create(name=skill_name)
    skills[skill_name] = skill

# Tạo Jobs
jobs_data = [
    {
        "title": "Senior Backend Developer",
        "company": company1,
        "description": "We are seeking a highly skilled Senior Backend Engineer...",
        "location": "Ho Chi Minh City",
        "job_type": "Full Time",
        "salary_min": 100,
        "salary_max": 150,
        "experience_level": "5+ years",
        "is_featured": True,
        "skill_names": ["Python", "Django", "PostgreSQL", "AWS"]
    },
    {
        "title": "Frontend Developer",
        "company": company2,
        "description": "Looking for a talented Frontend Developer to join our team...",
        "location": "Da Nang",
        "job_type": "Full Time",
        "salary_min": 70,
        "salary_max": 110,
        "experience_level": "3+ years",
        "is_featured": True,
        "skill_names": ["React", "JavaScript", "Docker"]
    },
    {
        "title": "DevOps Engineer",
        "company": company1,
        "description": "We need an experienced DevOps Engineer to manage our infrastructure...",
        "location": "Remote",
        "job_type": "Full Time",
        "salary_min": 90,
        "salary_max": 130,
        "experience_level": "4+ years",
        "is_featured": False,
        "skill_names": ["Docker", "Kubernetes", "AWS"]
    }
]

for job_data in jobs_data:
    skill_names = job_data.pop("skill_names")
    job, created = Job.objects.get_or_create(
        title=job_data["title"],
        company=job_data["company"],
        defaults=job_data
    )
    
    # Thêm skills
    for skill_name in skill_names:
        job.required_skills.add(skills[skill_name])
    
    status = "✅ Created" if created else "ℹ️ Already exists"
    print(f"{status}: {job.title}")

print("\n✅ Demo jobs added successfully!")