from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from jobs.models import Job, Application
from accounts.models import UserProfile
import json

@login_required(login_url='accounts:login')
def dashboard_index(request):
    """Employer dashboard"""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_employer():
        messages.error(request, 'Only employers can access dashboard!')
        return redirect('home')
    
    company = request.user.company
    
    # Statistics
    active_jobs = company.jobs.filter(is_active=True).count()
    total_applicants = Application.objects.filter(job__company=company).count()
    hired = Application.objects.filter(
        job__company=company,
        status='Accepted'
    ).count()
    
    # Recent job postings
    recent_jobs = company.jobs.all().order_by('-created_at')[:5]
    
    # Application statistics for chart
    applications_per_day = get_applications_per_day(company)
    job_category_data = get_job_category_data(company)
    
    context = {
        'company': company,
        'active_jobs': active_jobs,
        'total_applicants': total_applicants,
        'hired': hired,
        'recent_jobs': recent_jobs,
        'applications_per_day': json.dumps(applications_per_day),
        'job_category_data': json.dumps(job_category_data),
    }
    
    return render(request, 'dashboard/index.html', context)

def get_applications_per_day(company):
    """Get application statistics for last 7 days"""
    today = timezone.now().date()
    days = []
    data = []
    
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        day_name = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][date.weekday()]
        
        count = Application.objects.filter(
            job__company=company,
            created_at__date=date
        ).count()
        
        days.append(day_name)
        data.append(count)
    
    return {
        'labels': days,
        'data': data
    }

def get_job_category_data(company):
    """Get job postings by type"""
    job_types = company.jobs.values('job_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    labels = []
    data = []
    colors = ['#1a8a7a', '#2db8a6', '#ffc107', '#dc3545', '#6c757d']
    
    for i, item in enumerate(job_types[:5]):
        labels.append(item['job_type'] or 'Other')
        data.append(item['count'])
    
    return {
        'labels': labels,
        'data': data,
        'colors': colors[:len(labels)]
    }

@login_required(login_url='accounts:login')
def job_applications(request, pk):
    """View applications for a specific job"""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_employer():
        return redirect('home')
    
    job = get_object_or_404(Job, pk=pk, company=request.user.company)
    applications = job.applicants.all().order_by('-created_at')
    
    context = {
        'job': job,
        'applications': applications,
    }
    
    return render(request, 'dashboard/applications.html', context)

@login_required(login_url='accounts:login')
def update_application_status(request, app_id):
    """Update application status"""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_employer():
        return redirect('home')
    
    app = get_object_or_404(Application, pk=app_id, job__company=request.user.company)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['Pending', 'Reviewed', 'Accepted', 'Rejected']:
            app.status = status
            app.save()
            messages.success(request, 'Application status updated!')
    
    return redirect('dashboard:applications', pk=app.job.pk)