from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Job, Application, Skill
from accounts.models import UserProfile

def home(request):
    featured_jobs = Job.objects.filter(is_featured=True)[:6]
    return render(request, 'index.html', {
        'featured_jobs': featured_jobs
    })

def job_list(request):
    jobs = Job.objects.all()
    
    # Search filter
    search_query = request.GET.get('q', '')
    if search_query:
        jobs = jobs.filter(title__icontains=search_query)
    
    # Location filter
    location = request.GET.get('location', '')
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    # Job type filter
    job_type = request.GET.get('job_type', '')
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    job_types = Job.objects.values_list('job_type', flat=True).distinct()
    
    context = {
        'jobs': jobs,
        'job_types': job_types,
        'jobs_count': jobs.count(),
        'search_query': search_query,
        'search_location': location,
    }
    
    return render(request, 'jobs/list.html', context)

def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    
    # Check if user already applied
    user_applied = False
    if request.user.is_authenticated:
        user_applied = Application.objects.filter(
            user=request.user,
            job=job
        ).exists()
    
    context = {
        'job': job,
        'user_applied': user_applied
    }
    
    return render(request, 'jobs/detail.html', context)

@login_required(login_url='accounts:login')
def apply_job(request, pk):
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
def create_job(request):
    """Employer create job posting"""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_employer():
        messages.error(request, 'Only employers can post jobs!')
        return redirect('home')
    
    if request.method == 'POST':
        job = Job.objects.create(
            company=request.user.company,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            requirements=request.POST.get('requirements'),
            responsibilities=request.POST.get('responsibilities'),
            location=request.POST.get('location'),
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
    
    context = {
        'job_types': Job.JOB_TYPE_CHOICES
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
        job.title = request.POST.get('title', job.title)
        job.description = request.POST.get('description', job.description)
        job.requirements = request.POST.get('requirements', job.requirements)
        job.responsibilities = request.POST.get('responsibilities', job.responsibilities)
        job.location = request.POST.get('location', job.location)
        job.job_type = request.POST.get('job_type', job.job_type)
        job.salary_min = request.POST.get('salary_min') or job.salary_min
        job.salary_max = request.POST.get('salary_max') or job.salary_max
        job.experience_level = request.POST.get('experience_level', job.experience_level)
        job.save()
        
        messages.success(request, 'Job updated successfully!')
        return redirect('dashboard:index')
    
    context = {
        'job': job,
        'job_types': Job.JOB_TYPE_CHOICES
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