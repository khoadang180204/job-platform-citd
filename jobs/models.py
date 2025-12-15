from django.db import models
from django.conf import settings

class City(models.Model):
    """Model lưu các thành phố Việt Nam"""
    city = models.CharField(max_length=100, unique=True)
    province = models.CharField(max_length=100)
    area = models.CharField(max_length=50, blank=True, null=True)
    population = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['city']
        verbose_name_plural = 'Cities'
    
    def __str__(self):
        return self.city


class Skill(models.Model):
    """Model lưu các kỹ năng"""
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100, blank=True, null=True)  # IT, Marketing, etc.
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class JobCategory(models.Model):
    """Model lưu danh mục ngành nghề"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Job Categories'
    
    def __str__(self):
        return self.name


class JobPosition(models.Model):
    """Model lưu vị trí công việc (tên việc cụ thể)"""
    name = models.CharField(max_length=200, unique=True)
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE, related_name='positions')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Requirement(models.Model):
    """Model lưu các yêu cầu công việc"""
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
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, related_name='jobs')
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    salary_min = models.IntegerField(blank=True, null=True)
    salary_max = models.IntegerField(blank=True, null=True)
    required_skills = models.ManyToManyField(Skill, blank=True, related_name='jobs')
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
        """Backward compatibility"""
        return self.city.city if self.city else "Unknown"


class SavedJob(models.Model):
    """Model lưu các công việc mà Candidate đã lưu"""
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'job')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.job.title}"