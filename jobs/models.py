from django.db import models
from django.conf import settings

# Model lưu Tỉnh/Thành phố
class Province(models.Model):
    code = models.CharField(max_length=10, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=50)  # tinh, thanh-pho
    name_with_type = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Tỉnh/Thành phố'
        verbose_name_plural = 'Tỉnh/Thành phố'
    
    def __str__(self):
        return self.name_with_type

# Model lưu Quận/Huyện
class District(models.Model):
    code = models.CharField(max_length=10, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=50)  # quan, huyen, thi-xa, thanh-pho
    name_with_type = models.CharField(max_length=150)
    path = models.CharField(max_length=200, blank=True, null=True)
    path_with_type = models.CharField(max_length=300, blank=True, null=True)
    parent_code = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='districts', to_field='code')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Quận/Huyện'
        verbose_name_plural = 'Quận/Huyện'
    
    def __str__(self):
        return self.name_with_type

# Model lưu Xã/Phường
class Ward(models.Model):
    code = models.CharField(max_length=10, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=50)  # phuong, xa, thi-tran
    name_with_type = models.CharField(max_length=150)
    path = models.CharField(max_length=300, blank=True, null=True)
    path_with_type = models.CharField(max_length=400, blank=True, null=True)
    parent_code = models.ForeignKey(District, on_delete=models.CASCADE, related_name='wards', to_field='code')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Xã/Phường'
        verbose_name_plural = 'Xã/Phường'
    
    def __str__(self):
        return self.name_with_type

# Model lưu các kỹ năng
class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100, blank=True, null=True)  # IT, Marketing, etc.
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

# Model lưu danh mục ngành nghề
class JobCategory(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Job Categories'
    
    def __str__(self):
        return self.name

# Model lưu vị trí công việc (tên việc cụ thể)
class JobPosition(models.Model):
    name = models.CharField(max_length=200, unique=True)
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE, related_name='positions')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

# Model lưu các yêu cầu công việc
class Requirement(models.Model):
    REQUIREMENT_TYPES = [
        ('experience', 'Kinh nghiệm'),
        ('education_level', 'Trình độ học vấn'),
        ('language', 'Ngôn ngữ'),
        ('employment_type', 'Loại hình công việc'),
        ('work_mode', 'Hình thức làm việc'),
        ('gender', 'Giới tính'),
        ('age', 'Tuổi'),
        ('salary_range', 'Mức lương'),
        ('probation_time', 'Thời gian thử việc'),
        ('benefits', 'Phúc lợi'),
    ]
    
    requirement_type = models.CharField(max_length=50, choices=REQUIREMENT_TYPES)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['requirement_type', 'name']
        unique_together = ('requirement_type', 'name')
    
    def __str__(self):
        return f"{self.get_requirement_type_display()}: {self.name}"

# Model lưu thông tin doanh nghiệp
class Company(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='company'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    company_size = models.CharField(max_length=50, blank=True, null=True, help_text="Ví dụ: 25-99 nhân viên")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Companies'
    
    def __str__(self):
        return self.name
    
    def get_active_jobs_count(self):
        return self.jobs.filter(is_active=True).count()
    
    def get_total_applicants(self):
        return Application.objects.filter(job__company=self).count()
    
    def get_hired_count(self):
        return Application.objects.filter(job__company=self, status='Accepted').count()

# Model lưu thông tin việc làm
class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('Full Time', 'Full Time'),
        ('Part Time', 'Part Time'),
        ('Contract', 'Contract'),
        ('Remote', 'Remote'),
    ]
    
    title = models.CharField(max_length=200)
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    position = models.ForeignKey(JobPosition, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    description = models.TextField()
    requirements = models.TextField(blank=True, null=True)
    responsibilities = models.TextField(blank=True, null=True)
    # Location fields - phân cấp địa chỉ
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    address_detail = models.CharField(max_length=255, blank=True, null=True, help_text="Số nhà, tên đường, tòa nhà...")
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    salary_min = models.IntegerField(blank=True, null=True)
    salary_max = models.IntegerField(blank=True, null=True)
    required_skills = models.ManyToManyField(Skill, blank=True, related_name='jobs')
    job_requirements = models.ManyToManyField(Requirement, blank=True, related_name='jobs')
    experience_level = models.CharField(max_length=50, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expiration_date = models.DateField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def location(self):
        """Trả về địa chỉ đầy đủ hoặc từng phần"""
        parts = []
        if self.address_detail:
            parts.append(self.address_detail)
        if self.ward:
            parts.append(self.ward.name)
        if self.district:
            parts.append(self.district.name)
        if self.province:
            parts.append(self.province.name)
        return ', '.join(parts) if parts else "Không xác định"
    
    @property
    def location_short(self):
        """Trả về địa chỉ ngắn gọn (Quận/Huyện, Tỉnh/TP)"""
        parts = []
        if self.district:
            parts.append(self.district.name)
        if self.province:
            parts.append(self.province.name)
        return ', '.join(parts) if parts else "Không xác định"

# Model lưu các công việc mà Candidate đã lưu
class SavedJob(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_jobs'
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'job')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"

# Model lưu các ứng tuyển
class Application(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Reviewed', 'Reviewed'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applicants')
    cover_letter = models.TextField(blank=True, null=True)
    
    # Thông tin ứng viên
    full_name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    photo = models.ImageField(upload_to='applications/photos/', blank=True, null=True)
    cv_file = models.FileField(upload_to='applications/cv/', blank=True, null=True)
    introduction = models.TextField(blank=True, null=True, help_text='Giới thiệu bản thân ngắn gọn')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'job')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.job.title}"

# Model lưu hồ sơ kỹ năng của người dùng
# Hồ sơ kỹ năng của người dùng - dùng để matching với Job.
# Người dùng chọn categories và skills mình có để hệ thống tính điểm phù hợp.
class UserSkillProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='skill_profile'
    )
    
    # Categories và Skills mà người dùng có
    categories = models.ManyToManyField(JobCategory, blank=True, related_name='user_profiles')
    skills = models.ManyToManyField(Skill, blank=True, related_name='user_profiles')
    
    # Mô tả bản thân (optional) - dùng để TF-IDF matching với job description
    bio = models.TextField(blank=True, null=True, help_text="Mô tả ngắn về kinh nghiệm và kỹ năng của bạn")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Skill Profile'
        verbose_name_plural = 'User Skill Profiles'
    
    def __str__(self):
        return f"Skill Profile of {self.user.username}"
    
    def get_skills_text(self):
        """Trả về text của tất cả skills để dùng cho TF-IDF"""
        return ' '.join([skill.name for skill in self.skills.all()])
    
    def get_categories_text(self):
        """Trả về text của tất cả categories"""
        return ' '.join([cat.name for cat in self.categories.all()])