from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import UserProfile, PasswordResetOTP
from .email_service import send_otp_email, send_password_changed_email
from jobs.models import Company, SavedJob

# Xử lý yêu cầu đăng nhập
# Nếu người dùng đã đăng nhập, chuyển hướng đến trang chủ
# Nếu người dùng chưa đăng nhập, chuyển hướng đến trang đăng nhập
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Nếu người dùng là người tuyển dụng, chuyển hướng đến trang dashboard
            if hasattr(user, 'profile') and user.profile.is_employer():
                return redirect('dashboard:index')
            return redirect('home')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không chính xác!')
    
    return render(request, 'accounts/login.html')

# Xử lý yêu cầu đăng ký
# Nếu người dùng đã đăng nhập, chuyển hướng đến trang chủ
# Nếu người dùng chưa đăng nhập, chuyển hướng đến trang đăng ký
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role', '').lower()
        
        # Kiểm tra vai trò
        if role not in ['candidate', 'employer']:
            messages.error(request, 'Vui lòng chọn một loại tài khoản hợp lệ!')
            return render(request, 'accounts/register.html')
        
        # Kiểm tra mật khẩu
        if password1 != password2:
            messages.error(request, 'Mật khẩu không khớp!')
            return render(request, 'accounts/register.html')
        
        # Kiểm tra tên đăng nhập
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại!')
            return render(request, 'accounts/register.html')
        
        # Kiểm tra email
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email đã được đăng ký!')
            return render(request, 'accounts/register.html')
        
        # Tạo user với transaction
        try:
            with transaction.atomic():
                # Tạo user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name
                )
                
                # Tạo profile với vai trò
                profile = UserProfile.objects.create(
                    user=user,
                    role=role
                )
                
                # Nếu người dùng là người tuyển dụng, tạo profile công ty
                if role == 'employer':
                    Company.objects.create(
                        user=user,
                        name=first_name or username
                    )
                    messages.success(request, f'Chào mừng {first_name}! Tài khoản của bạn đã được tạo. Vui lòng đăng nhập để truy cập trang điều khiển.')
                else:
                    messages.success(request, f'Chào mừng {first_name}! Tài khoản của bạn đã được tạo. Vui lòng đăng nhập để tìm kiếm việc làm.')
                
                return redirect('accounts:login')
        
        except Exception as e:
            messages.error(request, f'Đăng ký thất bại: {str(e)}')
            return render(request, 'accounts/register.html')
    
    return render(request, 'accounts/register.html')

# Xử lý yêu cầu đăng xuất
def logout_view(request):
    logout(request)
    messages.success(request, 'Đăng xuất thành công!')
    return redirect('home')

# Xử lý yêu cầu cập nhật thông tin cá nhân
@login_required(login_url='accounts:login')
def profile_view(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        profile.bio = request.POST.get('bio', profile.bio)
        profile.phone = request.POST.get('phone', profile.phone)
        
        if request.FILES.get('avatar'):
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        messages.success(request, 'Thông tin cá nhân đã được cập nhật!')
    
    context = {
        'profile': profile,
    }
    
    # Nếu người dùng là người tuyển dụng, thêm thông tin công ty
    if profile.is_employer() and hasattr(request.user, 'company'):
        context['company'] = request.user.company
    
    return render(request, 'accounts/profile.html', context)

# Xử lý yêu cầu xem danh sách việc làm đã lưu
@login_required(login_url='accounts:login')
def saved_jobs_view(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_candidate():
        messages.error(request, 'Chỉ người tìm việc mới có thể lưu việc làm!')
        return redirect('home')
    
    saved_jobs = SavedJob.objects.filter(user=request.user).select_related('job').order_by('-created_at')
    
    context = {
        'saved_jobs': saved_jobs,
        'saved_jobs_count': saved_jobs.count()
    }
    
    return render(request, 'accounts/saved_jobs.html', context)

# Xử lý yêu cầu xem danh sách đơn ứng tuyển
@login_required(login_url='accounts:login')
def my_applications_view(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.is_candidate():
        messages.error(request, 'Chỉ người tìm việc mới có thể xem các đơn ứng tuyển!')
        return redirect('home')
    
    from jobs.models import Application
    applications = Application.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'applications': applications
    }
    
    return render(request, 'accounts/my_applications.html', context)

# Xử lý yêu cầu xem hồ sơ kỹ năng
@login_required(login_url='accounts:login')
def skill_profile_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if not user_profile.is_candidate():
        messages.error(request, 'Chỉ ứng viên mới có thể cập nhật hồ sơ kỹ năng!')
        return redirect('home')
    
    from jobs.models import UserSkillProfile, JobCategory, Skill
    
    # Lấy hoặc tạo skill profile
    skill_profile, created = UserSkillProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        bio = request.POST.get('bio', '')
        category_ids = request.POST.getlist('categories')
        skill_ids = request.POST.getlist('skills')
        
        # Cập nhật profile
        skill_profile.bio = bio
        skill_profile.save()
        
        # Cập nhật categories
        skill_profile.categories.set(category_ids)
        
        # Cập nhật skills
        skill_profile.skills.set(skill_ids)
        
        messages.success(request, 'Đã lưu hồ sơ kỹ năng thành công!')
        return redirect('accounts:skill_profile')
    
    # GET request
    categories = JobCategory.objects.all().order_by('name')
    skills = Skill.objects.all().order_by('category', 'name')
    
    # Lấy selected IDs
    selected_categories = list(skill_profile.categories.values_list('id', flat=True))
    selected_skills = list(skill_profile.skills.values_list('id', flat=True))
    
    context = {
        'profile': skill_profile,
        'categories': categories,
        'skills': skills,
        'selected_categories': selected_categories,
        'selected_skills': selected_skills,
    }
    
    return render(request, 'accounts/skill_profile.html', context)


# Xử lý yêu cầu quên mật khẩu
# Step 1: User nhập email để nhận OTP
def forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        
        if not email:
            messages.error(request, 'Vui lòng nhập địa chỉ email!')
            return render(request, 'accounts/forgot_password.html')
        
        # Kiểm tra email có tồn tại không
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Vẫn hiển thị thông báo thành công để bảo mật
            messages.success(request, 'Nếu email tồn tại trong hệ thống, bạn sẽ nhận được mã OTP.')
            return redirect('accounts:verify_otp')
        
        # Tạo OTP và gửi email
        otp_obj = PasswordResetOTP.generate_otp(email)
        
        # Gửi email
        if send_otp_email(email, otp_obj.otp):
            # Lưu email vào session để dùng ở bước tiếp theo
            request.session['reset_email'] = email
            messages.success(request, f'Mã OTP đã được gửi đến {email}. Vui lòng kiểm tra hộp thư!')
            return redirect('accounts:verify_otp')
        else:
            messages.error(request, 'Không thể gửi email. Vui lòng thử lại sau!')
    
    return render(request, 'accounts/forgot_password.html')

# Xử lý yêu cầu xác thực OTP
# Step 2: User nhập OTP để xác thực
def verify_otp_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    email = request.session.get('reset_email')
    
    if not email:
        messages.error(request, 'Phiên làm việc đã hết hạn. Vui lòng thử lại!')
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        otp_code = request.POST.get('otp', '').strip()
        
        if not otp_code or len(otp_code) != 6:
            messages.error(request, 'Vui lòng nhập mã OTP 6 số!')
            return render(request, 'accounts/verify_otp.html', {'email': email})
        
        # Xác thực OTP
        otp_obj = PasswordResetOTP.verify_otp(email, otp_code)
        
        if otp_obj:
            # Lưu trạng thái OTP đã xác thực
            request.session['otp_verified'] = True
            request.session['otp_id'] = otp_obj.id
            messages.success(request, 'Xác thực thành công! Vui lòng nhập mật khẩu mới.')
            return redirect('accounts:reset_password')
        else:
            messages.error(request, 'Mã OTP không đúng hoặc đã hết hạn!')
    
    return render(request, 'accounts/verify_otp.html', {'email': email})

# Xử lý yêu cầu reset mật khẩu
# Step 3: User nhập mật khẩu mới
def reset_password_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    email = request.session.get('reset_email')
    otp_verified = request.session.get('otp_verified')
    otp_id = request.session.get('otp_id')
    
    if not email or not otp_verified or not otp_id:
        messages.error(request, 'Phiên làm việc đã hết hạn. Vui lòng thử lại!')
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Kiểm tra mật khẩu
        if not password or len(password) < 6:
            messages.error(request, 'Mật khẩu phải có ít nhất 6 ký tự!')
            return render(request, 'accounts/reset_password.html')
        
        if password != confirm_password:
            messages.error(request, 'Mật khẩu xác nhận không khớp!')
            return render(request, 'accounts/reset_password.html')
        
        try:
            # Lấy user và đổi mật khẩu
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            
            # Đánh dấu OTP đã sử dụng
            try:
                otp_obj = PasswordResetOTP.objects.get(id=otp_id)
                otp_obj.is_used = True
                otp_obj.save()
            except PasswordResetOTP.DoesNotExist:
                pass
            
            # Gửi email thông báo
            send_password_changed_email(email)
            
            # Xóa session
            request.session.pop('reset_email', None)
            request.session.pop('otp_verified', None)
            request.session.pop('otp_id', None)
            
            messages.success(request, 'Mật khẩu đã được đổi thành công! Vui lòng đăng nhập.')
            return redirect('accounts:login')
            
        except User.DoesNotExist:
            messages.error(request, 'Không tìm thấy tài khoản!')
            return redirect('accounts:forgot_password')
    
    return render(request, 'accounts/reset_password.html')