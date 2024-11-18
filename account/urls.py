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
    UpdateRelationStatus,
    ContactDetails,
    RejectDependantView,
    DeleteContactView,
    UpdateContactView,
    # Trigger Emergency
    EmergencyActionView,
    # USSD
    USSDHandlerView
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
    path('contacts/<int:contact_id>/', ContactDetails.as_view(), name='contact-details'),
    path('update-status/', UpdateRelationStatus.as_view(), name='update-status'),
    path('approve-dependent/', ApproveDependantView.as_view(), name='approve-dependent'),
    path('reject-dependent/', RejectDependantView.as_view(), name='reject-dependent'),
    path('delete-contact/', DeleteContactView.as_view(), name='delete-contact'),
    path('update-contact/', UpdateContactView.as_view(), name='update-contact'),
    # Trigger Alerts
    path('trigger-alert/', EmergencyActionView.as_view(), name='trigger-alert'),
    # USSD
    path("ussd/", USSDHandlerView.as_view(), name="ussd-handler"),
    # Token refreshes
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
]
