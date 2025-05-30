from django.contrib import admin
from .models import AuthSecondFactor, UserSecondAuthenticationTestParams, OneTimePassword, UserPhone, UserProfile
# Register your models here.
admin.site.register(AuthSecondFactor)
admin.site.register(UserSecondAuthenticationTestParams)
admin.site.register(UserProfile)
admin.site.register(OneTimePassword)
admin.site.register(UserPhone)