from django.db import models
from django.conf import settings
from django.utils import timezone
import random
import string

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('candidate', 'Job Candidate'),
        ('employer', 'Employer'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='candidate')
    bio = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
    
    def is_employer(self):
        return self.role == 'employer'
    
    def is_candidate(self):
        return self.role == 'candidate'


class PasswordResetOTP(models.Model):
    """Model lưu mã OTP để đặt lại mật khẩu"""
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Password Reset OTP'
        verbose_name_plural = 'Password Reset OTPs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP for {self.email} - {'Used' if self.is_used else 'Active'}"
    
    @classmethod
    def generate_otp(cls, email, expiry_minutes=10):
        """Tạo OTP mới cho email"""
        # Xóa các OTP cũ chưa sử dụng của email này
        cls.objects.filter(email=email, is_used=False).delete()
        
        # Tạo mã OTP 6 số
        otp_code = ''.join(random.choices(string.digits, k=6))
        
        # Tạo thời gian hết hạn
        expires_at = timezone.now() + timezone.timedelta(minutes=expiry_minutes)
        
        # Lưu OTP
        otp_obj = cls.objects.create(
            email=email,
            otp=otp_code,
            expires_at=expires_at
        )
        
        return otp_obj
    
    def is_valid(self):
        """Kiểm tra OTP còn hiệu lực không"""
        return not self.is_used and timezone.now() < self.expires_at
    
    @classmethod
    def verify_otp(cls, email, otp_code):
        """Xác thực OTP"""
        try:
            otp_obj = cls.objects.get(email=email, otp=otp_code, is_used=False)
            if otp_obj.is_valid():
                return otp_obj
            return None
        except cls.DoesNotExist:
            return None