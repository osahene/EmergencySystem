import requests
import json
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.db import models
from datetime  import timedelta
from django.utils import timezone
import hashlib
from django.core.validators import EmailValidator
from django.conf import settings
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
import random
from django.urls import reverse
from django.core.mail import send_mail

OTP_EXPIRATION_TIME = 300  # 5 minutes
MAX_OTP_ATTEMPTS = 3

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email and password.
        """
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if not email:
            raise ValueError('Superusers must have an email address')
        if not password:
            raise ValueError('Superusers must have a password')

        return self.create_user(email, password, **extra_fields)


class AbstractUserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        validators=[EmailValidator()],  # Ensure valid email format
    )
    
    phone_number = models.CharField(max_length=20, unique=True)
    is_phone_verified = models.BooleanField(default=False)    
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # groups = models.ManyToManyField(
    #     'auth.Group',
    #     related_name='abstractuserprofile_groups',
    #     blank=True
    # )
    # user_permissions = models.ManyToManyField(
    #     'auth.Permission',
    #     related_name='abstractuserprofile_permissions',
    #     blank=True
    # )

    
    USERNAME_FIELD = 'email'
    
    objects = UserManager()
    
    class Meta:
        indexes = [
            models.Index(fields=['email'])
        ]
        # abstract = True

    def __str__(self):
        return self.email.lower()

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {'refresh': str(refresh), 'access': str(refresh.access_token)}
    
    def get_short_name(self):
        return self.email
    
    def get_subscription_level(self):
        if hasattr(self, 'users'):
            return self.users.subscription_level
        return None
    
    def get_fullname(self):
        if hasattr(self, 'users'):
            return f"{self.users.first_name} {self.users.last_name}"
        return None
    
class Users(AbstractUserProfile):
    SUBSCRIPTION_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('advance', 'Advance')
    ]
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    subscription_level = models.CharField(max_length=20, choices=SUBSCRIPTION_CHOICES, default='free')
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['first_name', 'last_name'])
        ]
        
    @property
    def get_full_name(self):
        return f"{self.first_name.title()} {self.last_name.title()}"
    
    def get_short_name(self):
        return self.first_name 
    
class Contacts(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email_address = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    relation = models.CharField(max_length=255)
    created_by = models.ForeignKey(Users, related_name='contacts', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    contact_user = models.ForeignKey(
        Users, 
        related_name='added_as_contact', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        indexes = [
            models.Index(fields=['first_name', 'last_name', 'email_address', 'phone_number'])
        ]
        ordering = ['-created_at']
    
    @property
    def get_full_name(self):
        return f"{self.first_name.title()} {self.last_name.title()}"
    

    def __str__(self):
        return f"{self.first_name} {self.last_name}" 

    def get_absolute_url(self):
        return reverse('contact-detail', kwargs={'pk': self.pk})   

class Emergency(models.Model):
    MISSION = [('success', 'Success'), ('failed', 'Failed')]
    
    created_by = models.ForeignKey(Users, related_name='emergency', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=10)
    location = models.JSONField(null=True, blank=True)
    usage_type = models.CharField(default='', max_length=100)
    location_context = models.CharField(max_length=200, null=True, blank=True, default='')
    country = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    town = models.CharField(max_length=100, null=True, blank=True)
    locality = models.CharField(max_length=100, null=True, blank=True)
    mission_status = models.CharField(max_length=20, choices=MISSION, default='')

class Institution(AbstractUserProfile):
    SERVICE_TYPE = [('police', 'Police'), ('fire', 'Fire'), ('nadmo', 'MADMO'), ('ecg', 'ECG')]
    institution_name = models.CharField(max_length=255)
    service = models.CharField(max_length=20, choices=SERVICE_TYPE, default='')
    class Meta:
        verbose_name = 'institution'
        verbose_name_plural = 'instituitions'
        indexes = [
            models.Index(fields=['institution_name'])
        ]

    def __str__(self):
        return self.company_name

    def get_absolute_url(self):
        return reverse('institution-detail', kwargs={'pk': self.pk})  

class OTP(models.Model):
    user = models.ForeignKey(Users, related_name='otps', on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=255)
    expiration_time = models.DateTimeField()
    failed_attempts = models.IntegerField(default=0)

    @staticmethod
    def hash_otp(otp_code):
        """Hash the OTP code before storing."""
        return hashlib.sha256(otp_code.encode()).hexdigest()

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))

    @staticmethod
    def create_otp(item):
        user = Users.objects.filter(email_address=item).first() if '@' in item else Users.objects.filter(phone_number=item).first()
        if not user:
            raise Exception("User with this phone number or email does not exist")
        
        otp_record = user.otps.first()
        if otp_record and timezone.now() < otp_record.expiration_time:
            cooldown_time = (otp_record.expiration_time - timezone.now()).seconds
            raise Exception(f"OTP already sent. Please wait {cooldown_time} seconds before requesting again.")
        
        otp_code = OTP.generate_otp()
        hashed_otp = OTP.hash_otp(otp_code)
        expiration_time = timezone.now() + timedelta(seconds=OTP_EXPIRATION_TIME)

        if otp_record:
            otp_record.otp_code = hashed_otp
            otp_record.expiration_time = expiration_time
            otp_record.failed_attempts = 0
            otp_record.save()
        else:
            OTP.objects.create(user=user, otp_code=hashed_otp, expiration_time=expiration_time)

        return otp_code

    @staticmethod
    def verify_otp(item, otp_code):
        user = Users.objects.filter(email_address=item).first() if '@' in item else Users.objects.filter(phone_number=item).first()
        if not user:
            raise Exception("User with this phone number or email does not exist")

        otp_record = user.otps.first()
        if not otp_record:
            raise Exception("OTP not found")

        if timezone.now() > otp_record.expiration_time:
            raise Exception("OTP expired")
        
        hashed_otp = OTP.hash_otp(otp_code)
        if otp_record.otp_code != hashed_otp:
            otp_record.failed_attempts += 1
            otp_record.save()
            if otp_record.failed_attempts >= MAX_OTP_ATTEMPTS:
                raise Exception("Too many failed attempts. Please request a new OTP.")
            raise Exception("Invalid OTP")

        otp_record.delete()
        return True

    @staticmethod
    def send_otp_email(email_address, message=None):
        otp_code = OTP.create_otp(email_address)
        print('otp code', otp_code)

        try:
            send_mail(
                subject="Email Verification OTP", 
                message=f"This is your email verification OTP{otp_code}",
                recipient_list=email_address,
                from_email=settings.DEFAULT_FROM_EMAIL,
                fail_silently=False
                )
            return Response({'message': 'OTP has been sent to your email'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return Response({'message': 'Error sending OTP'}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def send_sms(phone_number):
        otp_code = OTP.create_otp(phone_number)
        print('otp code', otp_code)
        post_data = {
                    "senderid": settings.WIGAL_SENDER_ID,
                    "destinations": [
                        {
                        "destination": phone_number,
                        "msgid": "MGS10101"
                        }
                    ],
                    "message": f"Your one-time password is: {otp_code}",
                    "smstype": "text"
                    }

        try:
            response = requests.post(
            'https://frogapi.wigal.com.gh/api/v3/sms/send',
            headers=settings.HEADERS,
            data=json.dumps(post_data)
        )
            return response.json()
           
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return Response({'message': 'Error sending OTP'}, status=status.HTTP_400_BAD_REQUEST)