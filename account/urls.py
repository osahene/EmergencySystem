from django.urls import path
from .views import (
    UserRegistrationView,
    LoginView,
    VerifyPhoneNumber,
    GenerateOTP,
    # Create User
    CreateRelation,
    UserContactsList,
    DependantView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('user-register/', UserRegistrationView.as_view(), name='user-register'),
    path('user-register-otp/', VerifyPhoneNumber.as_view(), name='user-register-otp'),
    path('user-login/', LoginView.as_view(), name='user-login'),
    # path('user-register-generate-otp/', RegisterGenerateOTP.as_view(), name='user-register-generate-otp'),
    path('user-register-generate-otp/', GenerateOTP.as_view(), name='user-generate-otp'),
    # path('user-login-otp/', ValidateLoginOTP.as_view(), name='user-login-otp'),
    path('create-relation/', CreateRelation.as_view(), name='create-relation'),
    path('my-contacts/', UserContactsList.as_view(), name='my-contacts'),
    path('my-dependants/', DependantView.as_view(), name='my-dependants'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
]
