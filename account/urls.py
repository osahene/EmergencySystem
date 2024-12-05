from django.urls import path
from .views import (
    UserRegistrationView,
    VerifyPhoneNumber,
    VerifyEmailAddress,
    LoginView,
    VerifyPhoneNumberOTP,
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
    # user auths
    path('user-register/', UserRegistrationView.as_view(), name='user-register'),
    path('verify-email/', VerifyEmailAddress.as_view(), name='verify-email'),
    path('verify-phone-number/', VerifyPhoneNumber.as_view(), name='verify-phone-number'),
    path('verify-phone-number-otp/', VerifyPhoneNumberOTP.as_view(), name='verify-phone-number-otp'),
    path('user-login/', LoginView.as_view(), name='user-login'),
    # Generate OTP
    path('user-register-generate-otp/', GenerateOTP.as_view(), name='user-generate-otp'),
    # create relations
    path('create-relation/', CreateRelation.as_view(), name='create-relation'),
    path('my-contacts/', UserContactsList.as_view(), name='my-contacts'),
    path('my-dependants/', DependantsListView.as_view(), name='my-dependants'),
    # Invitation Accept / reject
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
