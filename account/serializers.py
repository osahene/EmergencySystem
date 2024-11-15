from rest_framework import serializers
from django.core.validators import EmailValidator
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from .models import Users, Contacts
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[EmailValidator(message='Enter a valid email address')]
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[password_validation.validate_password]
    )
    phone_number = serializers.CharField(validators=[RegexValidator(regex=r'^\+\d{9,16}$')])

    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password']
        extra_kwargs = {'password': {'write_only': True, 'required':True}}
        
    def validate_email(self, value):
        """Check if email is already registered"""
        if Users.objects.filter(email=value).exists():
            raise ValidationError("A user with this email already exists.")
        elif Users.objects.filter(phone_number=value).exists():
            raise ValidationError("A user with this phone number already exists.")
        return value

    def create(self, validated_data):
        user = Users.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField(
        max_length=255, write_only=True
    )
    password = serializers.CharField(write_only=True)  # Access company name from related field
    phone_number = serializers.CharField(read_only=True)  # Access company name from related field
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    tokens = serializers.SerializerMethodField()
    
    class Meta:
        model = Users
        fields = [
            'email', 'password', 
            'phone_number', 
            'tokens', 'first_name', 'last_name'
            ]
    def get_tokens(self, obj):
        user = Users.objects.get(email=obj['email'])

        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }
        
    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        if '@' in email:
            validator = EmailValidator(message='Enter a valid email address')
            try:
                validator(email)
                user = authenticate(email=email, password=password)
                if user:
                    users = Users.objects.filter(email=email).first()
            except ValidationError:
                raise AuthenticationFailed('Enter a valid credential')
        else:
            user = authenticate(phone_number=email, password=password)
           
            if user:
                users = Users.objects.filter(phone_number=email).first()
        if not users:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not users.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        if not users.is_phone_verified:
            raise AuthenticationFailed('Phone number is not verified')

        return {
            'email': user.email,
            'phone_number': user.phone_number,
            'first_name': users.first_name,
            'last_name': users.last_name,
            'access': user.tokens()['access'],
            'refresh': user.tokens()['refresh']
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