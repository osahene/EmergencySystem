from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from django.core.validators import EmailValidator
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from .models import Users, Contacts, OTP
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from rest_framework.exceptions import APIException


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[EmailValidator(message='Enter a valid email address')]
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[password_validation.validate_password]
    )

    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True, 'required':True}}
        
    def validate_email(self, value):
        """Check if email is already registered"""
        if Users.objects.filter(email=value).exists():
            raise ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        user = Users.objects.create_user(**validated_data)
        return user
    
    
class CustomAuthenticationFailed(APIException):
    status_code = 307  # Temporary Redirect-like behavior
    default_detail = "Authentication failed."
    default_code = "authentication_failed"
    
    def __init__(self, detail=None, redirect_url=None):
        if detail is None:
            detail = self.default_detail
        self.detail = {"detail": detail}
        if redirect_url:
            self.detail["redirect_url"] = redirect_url
    
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=255, write_only=True)
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    is_phone_verified = serializers.BooleanField(read_only=True)
    tokens = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = [
            'email', 'password', 
            'phone_number', 
            'tokens', 'first_name', 'last_name', 'is_phone_verified'
        ]

    def get_tokens(self, obj):
        return {
            'tokens': obj['tokens']
        }

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        user = None

        if '@' in email:
            validator = EmailValidator(message='Enter a valid email address')
            try:
                validator(email)
            except ValidationError:
                raise AuthenticationFailed("Enter a valid email address.")
            user = authenticate(email=email, password=password)
            users = Users.objects.filter(email=email).first()
            
        else:
            user = authenticate(phone_number=email, password=password)
            users = Users.objects.filter(phone_number=email).first()

        if not user:
            raise AuthenticationFailed("Invalid credentials, try again.")

        if not user.is_active:
            raise AuthenticationFailed("Account disabled, contact admin.")
        
        if not user.is_verified:
            OTP.send_otp_email(user.email)
            raise CustomAuthenticationFailed(
                "Email not verified. A verification email has been sent.",
                redirect_url="/auth/email-verify"
            )

        # if not user.phone_number:
        #     raise CustomAuthenticationFailed(
        #         "Empty phone number.",
        #         redirect_url="/auth/phone-number"
        #     )

        # if not user.is_phone_verified:
        #     OTP.send_sms(user.phone_number)
        #     raise CustomAuthenticationFailed(
        #         "Phone number not verified. An OTP has been sent.",
        #         redirect_url="/auth/phone-number-verify"
        #     )
        return {
            'first_name': users.first_name,
            'last_name': users.last_name,
            'is_phone_verified': user.is_phone_verified,
            'tokens': user.tokens(),
        }

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacts
        fields = ['pk', 'first_name', 'last_name', 'email_address', 'phone_number', 'relation', 'status']
        
class ContactDependantSerializer(serializers.ModelSerializer):
    created_by_first_name = serializers.CharField(source='created_by.first_name')
    created_by_last_name = serializers.CharField(source='created_by.last_name')
    created_by_email = serializers.CharField(source='created_by.email')
    created_by_phone_number = serializers.CharField(source='created_by.phone_number')
    
    class Meta:
        model = Contacts
        fields = [
            'created_by_first_name', 
            'created_by_last_name', 
            'created_by_email',
            'created_by_phone_number',
            'relation', 
            'status'
            ]
        
class ContactStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacts
        fields = ['id', 'status']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        # Update the status of the contact
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance