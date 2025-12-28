from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from jobs.models import Job, Application, Company, Province, District, Ward, Skill, Requirement, JobCategory
from accounts.models import UserProfile
from accounts.decorators import employer_required
import json

# Lấy thông tin chung cho tất cả các view
def get_dashboard_context(request):
    company = request.user.company
    return {
        'company': company,
        'active_jobs_count': company.jobs.filter(is_active=True).count(),
        'pending_applications_count': Application.objects.filter(
            job__company=company, 
            status='Pending'
        ).count()
    }

# Trang tổng hợp
@login_required(login_url='accounts:login')
def dashboard_index(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_employer():
        messages.error(request, 'Chỉ người tuyển dụng mới có thể truy cập trang này!')
        return redirect('home')
    
    company = request.user.company
    
    # Thống kê
    active_jobs = company.jobs.filter(is_active=True).count()
    total_applicants = Application.objects.filter(job__company=company).count()
    hired = Application.objects.filter(job__company=company, status='Accepted').count()
    pending_count = Application.objects.filter(job__company=company, status='Pending').count()
    
    # Lấy 5 việc làm mới nhất
    recent_jobs = company.jobs.all().order_by('-created_at')[:5]
    
    # Chart data
    applications_per_day = get_applications_per_day(company)
    job_category_data = get_job_category_data(company)
    
    context = {
        **get_dashboard_context(request),
        'active_menu': 'overview',
        'active_jobs': active_jobs,
        'total_applicants': total_applicants,
        'hired': hired,
        'pending_count': pending_count,
        'recent_jobs': recent_jobs,
        'applications_per_day': json.dumps(applications_per_day),
        'job_category_data': json.dumps(job_category_data),
    }
    
    return render(request, 'dashboard/index.html', context)

# Lấy số lượng đơn ứng tuyển trong tuần
def get_applications_per_day(company):
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
    
    return {'labels': days, 'data': data}

# Lấy số lượng việc làm theo loại
def get_job_category_data(company):
    job_types = company.jobs.values('job_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    labels = []
    data = []
    
    for item in job_types[:5]:
        labels.append(item['job_type'] or 'Other')
        data.append(item['count'])
    
    return {'labels': labels, 'data': data}

# Quản lý các việc làm
@login_required(login_url='accounts:login')
def manage_jobs(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_employer():
        return redirect('home')
    
    company = request.user.company
    jobs = company.jobs.all().order_by('-created_at')
    
    context = {
        **get_dashboard_context(request),
        'active_menu': 'jobs',
        'jobs': jobs,
    }
    
    return render(request, 'dashboard/manage_jobs.html', context)

# Tạo việc làm mới
@login_required(login_url='accounts:login')
def create_job(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_employer():
        messages.error(request, 'Chỉ có tài khoản Người tuyển dụng mới có thể đăng bài. Nếu bạn chưa có tài khoản, hãy đăng ký ngay!')
        return redirect('home')
    
    if request.method == 'POST':
        # Lấy thông tin vị trí
        province = None
        district = None
        ward = None
        
        if request.POST.get('province'):
            province = get_object_or_404(Province, code=request.POST.get('province'))
        if request.POST.get('district'):
            district = get_object_or_404(District, code=request.POST.get('district'))
        if request.POST.get('ward'):
            ward = get_object_or_404(Ward, code=request.POST.get('ward'))
        
        category = None
        if request.POST.get('category'):
            category = get_object_or_404(JobCategory, id=request.POST.get('category'))
        
        job = Job.objects.create(
            company=request.user.company,
            title=request.POST.get('title'),
            category=category,
            description=request.POST.get('description'),
            requirements=request.POST.get('requirements_text'),
            responsibilities=request.POST.get('responsibilities'),
            province=province,
            district=district,
            ward=ward,
            address_detail=request.POST.get('address_detail', ''),
            job_type=request.POST.get('job_type'),
            salary_min=request.POST.get('salary_min') or None,
            salary_max=request.POST.get('salary_max') or None,
            experience_level=request.POST.get('experience_level'),
        )
        
        # Thêm skills
        skill_ids = request.POST.getlist('skills')
        if skill_ids:
            job.required_skills.set(skill_ids)
        
        # Thêm requirements
        requirement_ids = request.POST.getlist('job_requirements')
        if requirement_ids:
            job.job_requirements.set(requirement_ids)
        
        messages.success(request, 'Đăng việc thành công!')
        return redirect('dashboard:manage_jobs')
    
    # Lấy dữ liệu cho form
    categories = JobCategory.objects.all().order_by('name')
    provinces = Province.objects.all().order_by('name')
    skills = Skill.objects.all().order_by('category', 'name')
    requirements = Requirement.objects.all().order_by('requirement_type', 'name')
    experience_levels = Requirement.objects.filter(requirement_type='experience')
    
    context = {
        **get_dashboard_context(request),
        'active_menu': 'create_job',
        'categories': categories,
        'provinces': provinces,
        'skills': skills,
        'requirements': requirements,
        'experience_levels': experience_levels,
        'job_types': Job.JOB_TYPE_CHOICES,
    }
    
    return render(request, 'dashboard/create_job.html', context)

# Sửa việc làm
@login_required(login_url='accounts:login')
def edit_job(request, pk):
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_employer():
        return redirect('home')
    
    job = get_object_or_404(Job, pk=pk, company=request.user.company)
    
    if request.method == 'POST':
        # Lấy thông tin vị trí
        province = None
        district = None
        ward = None
        
        if request.POST.get('province'):
            province = get_object_or_404(Province, code=request.POST.get('province'))
        if request.POST.get('district'):
            district = get_object_or_404(District, code=request.POST.get('district'))
        if request.POST.get('ward'):
            ward = get_object_or_404(Ward, code=request.POST.get('ward'))
        
        category = None
        if request.POST.get('category'):
            category = get_object_or_404(JobCategory, id=request.POST.get('category'))
        
        job.title = request.POST.get('title')
        job.category = category
        job.description = request.POST.get('description')
        job.requirements = request.POST.get('requirements_text')
        job.responsibilities = request.POST.get('responsibilities')
        job.province = province
        job.district = district
        job.ward = ward
        job.address_detail = request.POST.get('address_detail', '')
        job.job_type = request.POST.get('job_type')
        job.salary_min = request.POST.get('salary_min') or None
        job.salary_max = request.POST.get('salary_max') or None
        job.experience_level = request.POST.get('experience_level')
        job.is_active = request.POST.get('is_active') == '1'
        job.save()
        
        # Cập nhật skills
        skill_ids = request.POST.getlist('skills')
        job.required_skills.set(skill_ids)
        
        # Cập nhật requirements
        requirement_ids = request.POST.getlist('job_requirements')
        job.job_requirements.set(requirement_ids)
        
        messages.success(request, 'Việc làm đã được cập nhật!')
        return redirect('dashboard:manage_jobs')
    
    # Lấy dữ liệu cho form
    categories = JobCategory.objects.all().order_by('name')
    provinces = Province.objects.all().order_by('name')
    skills = Skill.objects.all().order_by('category', 'name')
    requirements = Requirement.objects.all().order_by('requirement_type', 'name')
    experience_levels = Requirement.objects.filter(requirement_type='experience')
    
    # Lấy ID đã chọn
    selected_skills = list(job.required_skills.values_list('id', flat=True))
    selected_requirements = list(job.job_requirements.values_list('id', flat=True))
    
    # Lấy quận huyện và phường
    districts = []
    wards = []
    if job.province:
        districts = District.objects.filter(parent_code=job.province).order_by('name')
    if job.district:
        wards = Ward.objects.filter(parent_code=job.district).order_by('name')
    
    context = {
        **get_dashboard_context(request),
        'active_menu': 'jobs',
        'job': job,
        'categories': categories,
        'provinces': provinces,
        'districts': districts,
        'wards': wards,
        'skills': skills,
        'requirements': requirements,
        'experience_levels': experience_levels,
        'job_types': Job.JOB_TYPE_CHOICES,
        'selected_skills': selected_skills,
        'selected_requirements': selected_requirements,
    }
    
    return render(request, 'dashboard/edit_job.html', context)

# Xóa việc làm
@login_required(login_url='accounts:login')
def delete_job(request, pk):
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_employer():
        return redirect('home')
    
    job = get_object_or_404(Job, pk=pk, company=request.user.company)
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Xóa việc làm thành công!')
    
    return redirect('dashboard:manage_jobs')

# Xem tất cả đơn ứng tuyển
@login_required(login_url='accounts:login')
def all_applications(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_employer():
        return redirect('home')
    
    company = request.user.company
    applications = Application.objects.filter(job__company=company).order_by('-created_at')
    
    status = request.GET.get('status', '')
    if status:
        applications = applications.filter(status=status)
    
    total_count = Application.objects.filter(job__company=company).count()
    pending_count = Application.objects.filter(job__company=company, status='Pending').count()
    reviewed_count = Application.objects.filter(job__company=company, status='Reviewed').count()
    accepted_count = Application.objects.filter(job__company=company, status='Accepted').count()
    rejected_count = Application.objects.filter(job__company=company, status='Rejected').count()
    
    context = {
        **get_dashboard_context(request),
        'active_menu': 'applications',
        'applications': applications,
        'current_status': status,
        'total_count': total_count,
        'pending_count': pending_count,
        'reviewed_count': reviewed_count,
        'accepted_count': accepted_count,
        'rejected_count': rejected_count,
    }
    
    return render(request, 'dashboard/all_applications.html', context)


# Xem chi tiết đơn ứng tuyển
@login_required(login_url='accounts:login')
def application_detail(request, pk):
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_employer():
        return redirect('home')
    
    application = get_object_or_404(
        Application, 
        pk=pk, 
        job__company=request.user.company
    )
    
    context = {
        **get_dashboard_context(request),
        'active_menu': 'applications',
        'application': application,
    }
    
    return render(request, 'dashboard/application_detail.html', context)

# Xem tất cả đơn ứng tuyển cho một việc làm
@login_required(login_url='accounts:login')
def job_applications(request, pk):
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_employer():
        return redirect('home')
    
    job = get_object_or_404(Job, pk=pk, company=request.user.company)
    applications = job.applicants.all().order_by('-created_at')
    
    context = {
        **get_dashboard_context(request),
        'active_menu': 'jobs',
        'job': job,
        'applications': applications,
    }
    
    return render(request, 'dashboard/job_applications.html', context)

# Cập nhật trạng thái đơn ứng tuyển
@login_required(login_url='accounts:login')
def update_application_status(request, app_id):
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_employer():
        return redirect('home')
    
    app = get_object_or_404(Application, pk=app_id, job__company=request.user.company)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['Pending', 'Reviewed', 'Accepted', 'Rejected']:
            app.status = status
            app.save()
            messages.success(request, f'Đã cập nhật trạng thái đơn ứng tuyển thành {status}!')
    
    # Kiểm tra nơi để chuyển hướng
    next_url = request.POST.get('next', '')
    if 'detail' in next_url:
        return redirect('dashboard:application_detail', pk=app.id)
    
    return redirect('dashboard:all_applications')

# Cập nhật thông tin công ty
@login_required(login_url='accounts:login')
def company_settings(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_employer():
        return redirect('home')
    
    company = request.user.company
    
    if request.method == 'POST':
        company.name = request.POST.get('name', company.name)
        company.description = request.POST.get('description', company.description)
        company.website = request.POST.get('website', company.website)
        company.company_size = request.POST.get('company_size', company.company_size)
        
        if request.FILES.get('logo'):
            company.logo = request.FILES['logo']
        
        company.save()
        messages.success(request, 'Cập nhật thông tin doanh nghiệp thành công!')
    
    context = {
        **get_dashboard_context(request),
        'active_menu': 'settings',
    }
    
    return render(request, 'dashboard/company_settings.html', context)