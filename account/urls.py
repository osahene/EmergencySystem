from django.urls import path
from .views import (
    UserRegistrationView,
    LoginView,
    VerifyPhoneNumber,
    GenerateOTP,
    # Create User
    CreateRelation,
    UserContactsList,
    # DependantView,
    DependantsListView,
    ApproveDependantView,
    # approve_dependant,
    RejectDependantView,
    DeleteContactView,
    UpdateContactView,
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
    path('my-dependants/', DependantsListView.as_view(), name='my-dependants'),
    # path('approve-dependent/<int:pk>/', approve_dependant, name='approve-dependent'),
    path('approve-dependent/', ApproveDependantView.as_view(), name='approve-dependent'),
    path('reject-dependent/', RejectDependantView.as_view(), name='reject-dependent'),
    path('delete-contact/', DeleteContactView.as_view(), name='delete-contact'),
    path('update-contact/', UpdateContactView.as_view(), name='update-contact'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
]
