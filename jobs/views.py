from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Q
from .models import Job, Application, Skill, Province, District, Ward, SavedJob
from accounts.models import UserProfile

# Trang chủ
def home(request):
    from .models import JobCategory, UserSkillProfile
    from .matching_service import JobMatcher, get_user_skill_profile
    
    # Lấy jobs mới nhất
    latest_jobs = Job.objects.filter(is_active=True).order_by('-created_at')[:12]
    provinces = Province.objects.all().order_by('name')
    categories = JobCategory.objects.all().order_by('name')
    
    # Check skill profile và lấy matching jobs
    has_skill_profile = False
    matching_jobs = []
    
    if request.user.is_authenticated:
        try:
            skill_profile = UserSkillProfile.objects.get(user=request.user)
            # Kiểm tra xem user đã chọn ít nhất 1 skill hoặc category
            if skill_profile.skills.exists() or skill_profile.categories.exists():
                has_skill_profile = True
                
                # Lấy matching jobs
                matcher = JobMatcher(skill_profile)
                all_jobs = Job.objects.filter(is_active=True)
                matched_results = matcher.calculate_jobs_match(all_jobs)
                
                # Sắp xếp theo score giảm dần và lấy top 6 jobs có score > 0
                sorted_jobs = sorted(
                    [(job, matched_results[job.id]['matching_score']) for job in all_jobs if job.id in matched_results],
                    key=lambda x: x[1],
                    reverse=True
                )
                matching_jobs = [
                    {'job': job, 'score': score} 
                    for job, score in sorted_jobs 
                    if score > 0
                ][:6]
        except UserSkillProfile.DoesNotExist:
            pass
    
    return render(request, 'index.html', {
        'latest_jobs': latest_jobs,
        'provinces': provinces,
        'categories': categories,
        'has_skill_profile': has_skill_profile,
        'matching_jobs': matching_jobs,
    })

# Danh sách việc làm
def job_list(request):
    from .models import JobCategory, Requirement
    from .matching_service import JobMatcher, get_user_skill_profile
    
    jobs = Job.objects.filter(is_active=True)
    provinces = Province.objects.all().order_by('name')
    categories = JobCategory.objects.all()
    
    # Lấy các loại kinh nghiệm từ Requirement model
    experience_options = Requirement.objects.filter(requirement_type='experience').order_by('name')
    
    # Lấy các loại công việc từ Job model
    job_type_options = Job.JOB_TYPE_CHOICES
    
    # Tìm kiếm
    search_query = request.GET.get('q', '')
    if search_query:
        # Tìm kiếm trong title, description, requirements
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(requirements__icontains=search_query)
        )
    
    # Lọc theo nhiều tỉnh (cho thanh phan bên trái)
    provinces_list = request.GET.getlist('provinces')
    if provinces_list:
        jobs = jobs.filter(province_id__in=provinces_list)
    
    # Lọc theo tỉnh (cho thanh phan trên thanh menu)
    province_filter = request.GET.get('province_filter', '')
    if province_filter:
        jobs = jobs.filter(province_id=province_filter)
    
    # Lọc theo ngành nghề
    category_list = request.GET.getlist('category')
    if category_list:
        jobs = jobs.filter(category_id__in=category_list)
    
    # Lọc theo kinh nghiệm
    experience_list = request.GET.getlist('experience')
    if experience_list:
        jobs = jobs.filter(experience_level__in=experience_list)
    
    # Lọc theo mức lương
    salary_min = request.GET.get('salary_min', '')
    salary_max = request.GET.get('salary_max', '')
    if salary_min:
        jobs = jobs.filter(salary_min__gte=int(salary_min))
    if salary_max:
        jobs = jobs.filter(salary_max__lte=int(salary_max))
    
    # Lọc theo loại công việc (chế độ làm việc)
    job_types_list = request.GET.getlist('job_type')
    if job_types_list:
        jobs = jobs.filter(job_type__in=job_types_list)
    
    # Lấy các việc làm đã lưu và điểm phù hợp
    saved_job_ids = []
    matching_scores = {}  # Dict: job_id -> matching_info
    has_skill_profile = False
    
    if request.user.is_authenticated:
        saved_job_ids = list(SavedJob.objects.filter(user=request.user).values_list('job_id', flat=True))
        
        # Tính điểm phù hợp nếu user có skill profile
        user_profile = get_user_skill_profile(request.user)
        if user_profile and user_profile.skills.count() > 0:
            has_skill_profile = True
            matcher = JobMatcher(user_profile)
            matching_scores = matcher.calculate_jobs_match(jobs)
    
    # Sắp xếp
    sort_by = request.GET.get('sort', 'newest')
    
    if sort_by == 'matching' and has_skill_profile:
        # Sắp xếp theo điểm phù hợp (giá trị cao nhất)
        jobs_list = list(jobs)
        jobs_list.sort(key=lambda j: matching_scores.get(j.id, {}).get('matching_score', 0), reverse=True)
        jobs = jobs_list
    elif sort_by == 'oldest':
        jobs = jobs.order_by('created_at')
    elif sort_by == 'salary_high':
        jobs = jobs.order_by('-salary_max')
    elif sort_by == 'salary_low':
        jobs = jobs.order_by('salary_min')
    elif sort_by == 'city':
        jobs = jobs.order_by('province__name')
    else:  # newest (mặc định)
        jobs = jobs.order_by('-created_at')
    
    context = {
        'jobs': jobs,
        'provinces': provinces,
        'categories': categories,
        'experience_options': experience_options,
        'job_type_options': job_type_options,
        'jobs_count': len(jobs) if isinstance(jobs, list) else jobs.count(),
        'search_query': search_query,
        'province_filter': province_filter,
        'sort_by': sort_by,
        'selected_categories': category_list,
        'selected_experience': experience_list,
        'selected_job_types': job_types_list,
        'selected_provinces': provinces_list,
        'salary_min': salary_min,
        'salary_max': salary_max,
        'saved_job_ids': saved_job_ids,
        'matching_scores': matching_scores,
        'has_skill_profile': has_skill_profile,
    }
    
    return render(request, 'jobs/list.html', context)

# Chi tiết việc làm
def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    
    # Kiểm tra xem user đã apply hay chưa
    user_applied = False
    user_saved = False
    matching_info = None
    user_bio = ''
    
    if request.user.is_authenticated:
        user_applied = Application.objects.filter(
            user=request.user,
            job=job
        ).exists()
        user_saved = SavedJob.objects.filter(
            user=request.user,
            job=job
        ).exists()
        
        # Lấy CV matching info
        try:
            from .matching_service import get_job_matching_info
            matching_info = get_job_matching_info(job, request.user)
        except Exception as e:
            print(f"Matching error: {e}")
            matching_info = None
        
        # Lấy user bio từ profile để auto-fill
        try:
            if hasattr(request.user, 'profile') and request.user.profile.bio:
                user_bio = request.user.profile.bio
        except Exception:
            pass
    
    # Lấy các việc làm gợi ý cùng thành phố (province)
    related_jobs = []
    if job.province:
        related_jobs = Job.objects.filter(
            province=job.province,
            is_active=True
        ).exclude(pk=job.pk).order_by('-created_at')[:6]
    
    # Nếu không đủ 6 việc làm cùng tỉnh, lấy thêm từ category
    if len(related_jobs) < 6 and job.category:
        existing_ids = [j.pk for j in related_jobs]
        existing_ids.append(job.pk)
        more_jobs = Job.objects.filter(
            category=job.category,
            is_active=True
        ).exclude(pk__in=existing_ids).order_by('-created_at')[:6 - len(related_jobs)]
        related_jobs = list(related_jobs) + list(more_jobs)
    
    context = {
        'job': job,
        'user_applied': user_applied,
        'user_saved': user_saved,
        'related_jobs': related_jobs,
        'matching_info': matching_info,
        'user_bio': user_bio,
    }
    
    return render(request, 'jobs/detail.html', context)

# Áp dụng việc làm
@login_required(login_url='accounts:login')
def apply_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    profile = get_object_or_404(UserProfile, user=request.user)
    
    # Chỉ người tìm việc mới có thể ứng tuyển
    if not profile.is_candidate():
        messages.error(request, 'Chỉ người tìm việc mới có thể ứng tuyển!')
        return redirect('jobs:detail', pk=job.pk)
    
    if request.method == 'POST':
        # Kiểm tra xem user đã apply hay chưa
        if Application.objects.filter(user=request.user, job=job).exists():
            messages.warning(request, 'Bạn đã ứng tuyển cho việc này rồi!')
            return redirect('jobs:detail', pk=job.pk)
        
        # Lấy form data
        full_name = request.POST.get('full_name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        introduction = request.POST.get('introduction', '')
        cover_letter = request.POST.get('cover_letter', '')
        
        # Tạo ứng tuyển
        application = Application.objects.create(
            user=request.user,
            job=job,
            full_name=full_name,
            email=email,
            phone=phone,
            introduction=introduction,
            cover_letter=cover_letter
        )
        
        # Xử lý file upload
        if request.FILES.get('photo'):
            application.photo = request.FILES['photo']
        
        if request.FILES.get('cv_file'):
            application.cv_file = request.FILES['cv_file']
        
        application.save()
        
        messages.success(request, 'Đã gửi đơn ứng tuyển! Người tuyển dụng sẽ xem xét đơn của bạn.')
        return redirect('jobs:detail', pk=job.pk)
    
    return redirect('jobs:detail', pk=job.pk)

# Lưu việc làm
@login_required(login_url='accounts:login')
def save_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_candidate():
        messages.error(request, 'Chỉ người tìm việc mới có thể lưu việc làm!')
        # Quay lại trang trước đó
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('jobs:detail', pk=job.pk)
    
    saved_job, created = SavedJob.objects.get_or_create(
        user=request.user,
        job=job
    )
    
    if created:
        messages.success(request, 'Đã lưu việc làm!')
    else:
        saved_job.delete()
        messages.success(request, 'Đã bỏ lưu việc làm!')
    
    # Quay lại trang trước đó
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('jobs:detail', pk=job.pk)

# Đăng việc làm
@login_required(login_url='accounts:login')
def create_job(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_employer():
        messages.error(request, 'Chỉ người tuyển dụng mới có thể đăng việc làm!')
        return redirect('home')
    
    if request.method == 'POST':
        # Lấy thông tin địa lý
        province = None
        district = None
        ward = None
        
        if request.POST.get('province'):
            province = get_object_or_404(Province, code=request.POST.get('province'))
        if request.POST.get('district'):
            district = get_object_or_404(District, code=request.POST.get('district'))
        if request.POST.get('ward'):
            ward = get_object_or_404(Ward, code=request.POST.get('ward'))
        
        job = Job.objects.create(
            company=request.user.company,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            requirements=request.POST.get('requirements'),
            responsibilities=request.POST.get('responsibilities'),
            province=province,
            district=district,
            ward=ward,
            job_type=request.POST.get('job_type'),
            salary_min=request.POST.get('salary_min') or None,
            salary_max=request.POST.get('salary_max') or None,
            experience_level=request.POST.get('experience_level'),
        )
        
        # Thêm skill nếu có
        skills_str = request.POST.get('required_skills', '')
        if skills_str:
            skill_names = [s.strip() for s in skills_str.split(',')]
            for skill_name in skill_names:
                skill, _ = Skill.objects.get_or_create(name=skill_name)
                job.required_skills.add(skill)
        
        messages.success(request, 'Đăng việc thành công!')
        return redirect('dashboard:index')
    
    provinces = Province.objects.all().order_by('name')
    context = {
        'job_types': Job.JOB_TYPE_CHOICES,
        'provinces': provinces
    }
    
    return render(request, 'jobs/create.html', context)

# Chỉnh sửa việc làm
@login_required(login_url='accounts:login')
def edit_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_employer() or job.company.user != request.user:
        messages.error(request, 'Chỉ người tuyển dụng mới có thể chỉnh sửa việc làm của mình!')
        return redirect('home')
    
    if request.method == 'POST':
        # Lấy thông tin địa lý
        province = None
        district = None
        ward = None
        
        if request.POST.get('province'):
            province = get_object_or_404(Province, code=request.POST.get('province'))
        if request.POST.get('district'):
            district = get_object_or_404(District, code=request.POST.get('district'))
        if request.POST.get('ward'):
            ward = get_object_or_404(Ward, code=request.POST.get('ward'))
        
        job.title = request.POST.get('title', job.title)
        job.description = request.POST.get('description', job.description)
        job.requirements = request.POST.get('requirements', job.requirements)
        job.responsibilities = request.POST.get('responsibilities', job.responsibilities)
        job.province = province
        job.district = district
        job.ward = ward
        job.job_type = request.POST.get('job_type', job.job_type)
        job.salary_min = request.POST.get('salary_min') or job.salary_min
        job.salary_max = request.POST.get('salary_max') or job.salary_max
        job.experience_level = request.POST.get('experience_level', job.experience_level)
        job.save()
        
        messages.success(request, 'Đã cập nhật thông tin việc làm!')
        return redirect('dashboard:index')
    
    provinces = Province.objects.all().order_by('name')
    context = {
        'job': job,
        'job_types': Job.JOB_TYPE_CHOICES,
        'provinces': provinces
    }
    
    return render(request, 'jobs/edit.html', context)

# Xóa việc làm
@login_required(login_url='accounts:login')
@require_http_methods(["POST"])
def delete_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_employer() or job.company.user != request.user:
        messages.error(request, 'Chỉ người tuyển dụng mới có thể xóa việc làm của mình!')
        return redirect('home')
    
    job.delete()
    messages.success(request, 'Đã xóa việc làm!')
    return redirect('dashboard:index')

# Lấy danh sách Quận/Huyện theo mã Tỉnh/Thành phố
def get_districts(request, province_code):
    districts = District.objects.filter(parent_code=province_code).order_by('name')
    data = [
        {
            'code': d.code,
            'name': d.name,
            'name_with_type': d.name_with_type,
        }
        for d in districts
    ]
    return JsonResponse({'districts': data})

# Lấy danh sách Xã/Phường theo mã Quận/Huyện
def get_wards(request, district_code):
    wards = Ward.objects.filter(parent_code=district_code).order_by('name')
    data = [
        {
            'code': w.code,
            'name': w.name,
            'name_with_type': w.name_with_type,
        }
        for w in wards
    ]
    return JsonResponse({'wards': data})

# Lấy danh sách Skills theo JobCategory
def get_skills_by_category(request, category_id):
    from .models import JobCategory, Skill
    
    try:
        category = JobCategory.objects.get(id=category_id)
        # Lấy skills mà category_name chứa tên category hoặc tương đương
        # Nếu skill.category khớp với tên JobCategory thì hiển thị
        skills = Skill.objects.filter(category__icontains=category.name).order_by('name')
        
        # Nếu không có skill nào khớp, trả về tất cả skills
        if not skills.exists():
            skills = Skill.objects.all().order_by('category', 'name')
        
        data = [
            {
                'id': s.id,
                'name': s.name,
                'category': s.category or 'Other',
            }
            for s in skills
        ]
        return JsonResponse({'skills': data, 'category_name': category.name})
    except JobCategory.DoesNotExist:
        return JsonResponse({'skills': [], 'error': 'Không tìm thấy danh mục'}, status=404)