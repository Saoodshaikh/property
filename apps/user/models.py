
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import  RegexValidator, MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timezone
from django.conf import settings
import random

# Custom User Manager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(" The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
        
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

    
class CustomUser(AbstractBaseUser):
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('tenant', 'Tenant'),
        ('ca', 'CA'),
        ('property_manager', 'Property Manager'),
        ('legal_advisor', 'Legal Advisor'),
        ('agent_broker', 'Agent Broker'),

    )
    GENDER_CHOICES = (
        ('male','Male'),
        ('female', 'Female')
    )
    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=30, null=False, blank=False)
    last_name = models.CharField(max_length=30, null=False, blank=False)
    roll = models.CharField(choices=ROLE_CHOICES, null=False, blank=False)
    phone_number = models.CharField(
        max_length=15, blank=False, null=False, validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message='Phone number is must be upto 15 numbers')
                                                                           ])
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=150, null=True,blank=True)
    gender = models.CharField(choices=GENDER_CHOICES, blank=True, null=True)
    bank_account_info = models.CharField(max_length=255, blank=False, null=False)
    tax_id = models.CharField(max_length=55, null=False, blank=False)
    kyc_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        ordering = ['email']
        verbose_name = "User"
        verbose_name_plural = "Users"
        unique_together = (('first_name', 'last_name'),)
    
        
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def clean(self):
        if self.kyc_verified and not self.tax_id:
            raise ValidationError("tax ID must be verified if KYC is verified")
        if len(self.phone_number) < 10:
            raise ValidationError("Phone Number must be greater than 10")
        
        if self.roll == 'owner' and not self.bank_account_info:
            raise ValidationError("Owner must have a bank account")
        
        if self.roll == 'tenant' and not self.bank_account_info:
            raise ValidationError("Tenant must have a bank account")
    
    def validate_tax_id(value):
        if len(value) < 2:
            raise ValueError('Tax ID must be greater than 2 didgit')
        
    # create a userprofile for signals
class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    personal_info = models.JSONField(default=dict)
    account_info = models.JSONField(default=dict)

# Signal to create Profile for user after creation


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.roll in ['owner', 'tenant', '']:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=CustomUser)
def update_user_profile(sender, instance, **kwargs):
    if instance.roll in ['owner','tenant', 'property_manager', 'legal_advisor']:
        UserProfile.objects.update_or_create(user=instance)

    
""" All the KYC related fields and table define below"""

class UserKYC(models.Model):
    KYC_CHOICES =(
        ('aadhar_card', 'Aadhar card'),
        ('pan_card', 'Pan card')
    )
    STATUS= (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected')
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    aadhar_card_number = models.CharField(max_length=12, null=True, blank=True, unique=True, 
                                          validators=[
            MinLengthValidator(12),  # Minimum length of 12
            MaxLengthValidator(12),  # Maximum length of 12
            RegexValidator(r'^\d{12}$', 'Aadhaar number must be exactly 12 digits.')  # Regex for exact 12 digits
        ])
    pan_card_number = models.CharField(max_length=10, blank=True, null=True, unique=True)
    is_verified = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS, default='pending')
    verification_method = models.CharField(max_length=11, choices=KYC_CHOICES)
    submission_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        
        if self.verification_method=='aadhar_card':
            if not self.aadhar_card_number:
                raise ValueError("Adhar details must be provided for Aadhar verification")
        
        elif self.verification_method=='pan_card':
            if not self.pan_card_number:
                raise ValueError("Pan card details must be provieded for Pan card Verification")
    
        
        # Automatic handling of status based on verification
        # if self.is_verified:
        #     self.status = 'verified'
        # else:
        #     self.status = 'pending'

        # super(UserKYC, self).save(*args, **kwargs)
    
    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.otp_created_at = timezone.now()
        self.otp_expires_at = timezone.now() + timezone.timedelta(minutes=10)
        self.save()
    
    def verify_otp(self, entered_otp):
        if timezone.now() > self.otp_expires_at:
            return False, "OTP has expired"
        
        if self.otp != entered_otp:
            return False, " Invalid OTP"
        
        return True, "OTP has verified"
    
    def verified(self):
        if self.is_verified:
            self.status = 'verified'
        else:
            self.status = 'pending'

    def __str__(self):
        return f"Kyc for {self.user} -staus{self.status}"







    

    



