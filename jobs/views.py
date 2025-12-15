from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import Job, Application, Skill, City, SavedJob
from accounts.models import UserProfile

def home(request):
    featured_jobs = Job.objects.filter(is_featured=True, is_active=True)[:6]
    cities = City.objects.all().order_by('city')
    return render(request, 'index.html', {
        'featured_jobs': featured_jobs,
        'cities': cities
    })

def job_list(request):
    """Jobs list với search và filter"""
    jobs = Job.objects.filter(is_active=True)
    cities = City.objects.all()
    
    # Search by keyword
    search_query = request.GET.get('q', '')
    if search_query:
        # Tìm kiếm trong title, description, requirements
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(requirements__icontains=search_query)
        )
    
    # Filter by multiple cities
    cities_list = request.GET.getlist('cities')  # Get multiple cities
    city_id = request.GET.get('city', '')  # Legacy single city filter
    
    if cities_list:
        jobs = jobs.filter(city_id__in=cities_list)
    elif city_id:
        jobs = jobs.filter(city_id=city_id)
    
    # Filter by job type
    job_type = request.GET.get('job_type', '')
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    # Get unique job types for filter
    job_types = Job.objects.values_list('job_type', flat=True).distinct()
    
    # Get user's saved jobs
    saved_job_ids = []
    if request.user.is_authenticated:
        saved_job_ids = list(SavedJob.objects.filter(user=request.user).values_list('job_id', flat=True))
    
    context = {
        'jobs': jobs,
        'cities': cities,
        'job_types': job_types,
        'jobs_count': jobs.count(),
        'search_query': search_query,
        'city_id': city_id,
        'saved_job_ids': saved_job_ids,
    }
    
    return render(request, 'jobs/list.html', context)

def job_detail(request, pk):
    """Job detail view"""
    job = get_object_or_404(Job, pk=pk)
    
    # Check if user already applied
    user_applied = False
    user_saved = False
    if request.user.is_authenticated:
        user_applied = Application.objects.filter(
            user=request.user,
            job=job
        ).exists()
        user_saved = SavedJob.objects.filter(
            user=request.user,
            job=job
        ).exists()
    
    context = {
        'job': job,
        'user_applied': user_applied,
        'user_saved': user_saved
    }
    
    return render(request, 'jobs/detail.html', context)

@login_required(login_url='accounts:login')
def apply_job(request, pk):
    """Apply for a job"""
    job = get_object_or_404(Job, pk=pk)
    profile = get_object_or_404(UserProfile, user=request.user)
    
    # Only candidates can apply
    if not profile.is_candidate():
        messages.error(request, 'Only candidates can apply for jobs!')
        return redirect('jobs:detail', pk=job.pk)
    
    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter', '')
        
        # Check if already applied
        if Application.objects.filter(user=request.user, job=job).exists():
            messages.warning(request, 'You already applied for this job!')
            return redirect('jobs:detail', pk=job.pk)
        
        # Create application
        application = Application.objects.create(
            user=request.user,
            job=job,
            cover_letter=cover_letter
        )
        
        messages.success(request, 'Application submitted successfully!')
        return redirect('jobs:detail', pk=job.pk)
    
    return render(request, 'jobs/detail.html', {'job': job})

@login_required(login_url='accounts:login')
def save_job(request, pk):
    """Save/Unsave a job"""
    job = get_object_or_404(Job, pk=pk)
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_candidate():
        messages.error(request, 'Only candidates can save jobs!')
        return redirect('jobs:detail', pk=job.pk)
    
    saved_job, created = SavedJob.objects.get_or_create(
        user=request.user,
        job=job
    )
    
    if created:
        messages.success(request, 'Job saved successfully!')
    else:
        saved_job.delete()
        messages.success(request, 'Job removed from saved!')
    
    return redirect('jobs:detail', pk=job.pk)

@login_required(login_url='accounts:login')
def create_job(request):
    """Employer create job posting"""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_employer():
        messages.error(request, 'Only employers can post jobs!')
        return redirect('home')
    
    if request.method == 'POST':
        city_id = request.POST.get('city')
        city = get_object_or_404(City, id=city_id)
        
        job = Job.objects.create(
            company=request.user.company,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            requirements=request.POST.get('requirements'),
            responsibilities=request.POST.get('responsibilities'),
            city=city,
            job_type=request.POST.get('job_type'),
            salary_min=request.POST.get('salary_min') or None,
            salary_max=request.POST.get('salary_max') or None,
            experience_level=request.POST.get('experience_level'),
        )
        
        # Add skills if provided
        skills_str = request.POST.get('required_skills', '')
        if skills_str:
            skill_names = [s.strip() for s in skills_str.split(',')]
            for skill_name in skill_names:
                skill, _ = Skill.objects.get_or_create(name=skill_name)
                job.required_skills.add(skill)
        
        messages.success(request, 'Job posted successfully!')
        return redirect('dashboard:index')
    
    cities = City.objects.all()
    context = {
        'job_types': Job.JOB_TYPE_CHOICES,
        'cities': cities
    }
    
    return render(request, 'jobs/create.html', context)

@login_required(login_url='accounts:login')
def edit_job(request, pk):
    """Employer edit job posting"""
    job = get_object_or_404(Job, pk=pk)
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_employer() or job.company.user != request.user:
        messages.error(request, 'You can only edit your own jobs!')
        return redirect('home')
    
    if request.method == 'POST':
        city_id = request.POST.get('city')
        city = get_object_or_404(City, id=city_id)
        
        job.title = request.POST.get('title', job.title)
        job.description = request.POST.get('description', job.description)
        job.requirements = request.POST.get('requirements', job.requirements)
        job.responsibilities = request.POST.get('responsibilities', job.responsibilities)
        job.city = city
        job.job_type = request.POST.get('job_type', job.job_type)
        job.salary_min = request.POST.get('salary_min') or job.salary_min
        job.salary_max = request.POST.get('salary_max') or job.salary_max
        job.experience_level = request.POST.get('experience_level', job.experience_level)
        job.save()
        
        messages.success(request, 'Job updated successfully!')
        return redirect('dashboard:index')
    
    cities = City.objects.all()
    context = {
        'job': job,
        'job_types': Job.JOB_TYPE_CHOICES,
        'cities': cities
    }
    
    return render(request, 'jobs/edit.html', context)

@login_required(login_url='accounts:login')
@require_http_methods(["POST"])
def delete_job(request, pk):
    """Employer delete job posting"""
    job = get_object_or_404(Job, pk=pk)
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_employer() or job.company.user != request.user:
        messages.error(request, 'You can only delete your own jobs!')
        return redirect('home')
    
    job.delete()
    messages.success(request, 'Job deleted successfully!')
    return redirect('dashboard:index')