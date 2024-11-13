# authentication/backends.py

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOrPhoneBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, phone_number=None):
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return None
        elif phone_number:
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                return None
        else:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def user_can_authenticate(self, user):
        return user.is_active
