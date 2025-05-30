from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField 

from django.utils import timezone
from django.apps import apps 
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import transaction
from django.apps import apps ### Модельді атынан алу үшін
from django.contrib.postgres.fields import JSONField 
from django.db.models.signals import post_save
from django.dispatch import receiver
import traceback
import time as os_calc_time # Функцияларды орындау жылдамдығын тексеру үшін логгерде

import logging
logger = logging.getLogger('developer')

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Пайдаланушы профилі туралы қосымша ақпаратты сақтау үшін модель
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Негізгі User моделімен байланыс
    approved = models.BooleanField(default=False)  # Аккаунттың расталғанын көрсету үшін қолданылатын өріс

    def __str__(self):
        return f"{self.user.username} - {'Approved' if self.approved else 'Not Approved'}"

# Екінші факторлық аутентификация параметрлерін сақтау үшін модель
class AuthSecondFactor(models.Model):
    SECOND_FACTOR_CHOICES = [
        ('OTP', 'One Time Password to Email'),  # Бір реттік құпиясөз
        ('Quiz', 'Quiz'),  # Қосымша сұрақ-жауап
        ('Test', 'Test'),  # Арнайы тест
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Пайдаланушымен байланыс
    active = models.BooleanField(default=True)  # Екінші фактордың белсенділігін анықтау
    second_factor = models.CharField(max_length=50, choices=SECOND_FACTOR_CHOICES)  # Пайдаланушы таңдаған әдіс
    passvalue = models.CharField(max_length=255, blank=True)  # Екінші факторға байланысты деректер

    def __str__(self):
        return f"{self.user.username} - {self.get_second_factor_display()}"

# Арнайы тест параметрлерін сақтау үшін модель
class UserSecondAuthenticationTestParams(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Пайдаланушымен байланыс
    default = models.BooleanField(default=False)  # Арнайы тесттің әдепкі қолданылатынын көрсету
    value_chain = models.JSONField()  # Қозғалыстар тізбегі немесе координаттар

    def __str__(self):
        return f"{self.user.username} - {'Default' if self.default else 'Inactive'} Special Test"

# Бір реттік құпиясөздерді (OTP) сақтау үшін модель
class OneTimePassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Пайдаланушымен байланыс
    phone_number = models.CharField(max_length=30)  # Пайдаланушының телефон нөмірі
    confirmation_code = models.CharField(max_length=6)  # Бір реттік құпиясөз (OTP)
    created_at = models.DateTimeField(default=timezone.now)  # Құпиясөздің жасалу уақыты

    def is_valid(self):
        print(f'OTP: {self.pk} валидность: время: {timezone.now()}; создано: {self.created_at}')
        return timezone.now() < self.created_at + timezone.timedelta(minutes=3)

    def __str__(self):
        return f"{self.user.username} - {self.confirmation_code} ({self.created_at})"
    @staticmethod
    def delete_expired_passwords():
        # Барлық мерзімі өткен бір реттік құпиясөздерді жою
        expired_passwords = OneTimePassword.objects.filter(created_at__lt=timezone.now() - timezone.timedelta(minutes=3))
        expired_passwords.delete()

    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    userprofile, created = UserProfile.objects.get_or_create(user=instance)
    if created:
        logger.debug(f'Профиль пользователя создан: {userprofile}')
    else:
        logger.debug(f'Профиль пользователя уже существует: {userprofile}')


# Пайдаланушы телефон нөмірлерін сақтау үшін модель
class UserPhone(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)  # Пайдаланушымен байланыс
    phone = models.CharField("Телефон", max_length=20)  # Пайдаланушының телефон нөмірі
    enabled = models.BooleanField("доступен", default=True)  # Белсенді нөмір екенін көрсету

    def __str__(self):
        return f"{self.user.username} - {self.phone} ({'Enabled' if self.enabled else 'Disabled'})"

# @receiver(pre_save, sender=UserPhone)
# def ensure_single_enabled(sender, instance, **kwargs):
#     # Объект UserPhone сақтаған кезде, осы пайдаланушы үшін басқа enabled=True жазбалар жоқ екенін тексереміз
#     if instance.enabled:
#         existing_enabled_phones = UserPhone.objects.filter(user=instance.user, enabled=True).exclude(pk=instance.pk)
#         if existing_enabled_phones.exists():
#             # Егер мұндай жазбалар болса, оларды өшіреміз, enabled=False орната отырып
#             existing_enabled_phones.update(enabled=False)
