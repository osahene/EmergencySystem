from django.contrib import admin
from .models import Users, Institution, Contacts, AbstractUserProfile, OTP
# Register your models here.
admin.site.register(OTP)
admin.site.register(Users)
admin.site.register(Institution)
admin.site.register(Contacts)
admin.site.register(AbstractUserProfile)
