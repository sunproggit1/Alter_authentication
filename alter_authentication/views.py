import json
import hashlib
import random
from django.shortcuts import render
from django.views import View
from django.contrib.auth import logout
from django.shortcuts import redirect,render, get_object_or_404
from django_ratelimit.decorators import ratelimit

from django.urls import reverse
from django.shortcuts import get_object_or_404
from urllib.parse import urlencode, urljoin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.crypto import get_random_string

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.views.decorators.http import require_POST, require_http_methods

from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView, PasswordResetCompleteView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetView
from django.contrib.auth import login as additional_login # стандартный логин
from django.db import transaction # для транзакций

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import FormView, ListView, DetailView, CreateView, UpdateView
from django.apps import apps ### взять модель по имени

from django.views.decorators.csrf import ensure_csrf_cookie
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView ## для переопределения логики логина
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import ValidationError
from django.db import IntegrityError, DatabaseError
# Create your views here.
from datetime import datetime, timedelta, timezone # #работы с датой
from django import forms
from django.shortcuts import redirect
from functools import wraps
from django.core.mail import send_mail

from .models import OneTimePassword, UserPhone, AuthSecondFactor, UserSecondAuthenticationTestParams
from .forms import CustomUserCreationForm, OneTimePasswordForm, TwoFactorAuthForm
from .forms import EmailVerificationForm  # Форма для ввода кода


# Пайдаланушыдан CSRF токен алу үшін
@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'new_csrf_token': request.META.get('CSRF_COOKIE')})


# Пайдаланушы профилін тексеру декораторы
def check_approved(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Егер пайдаланушы расталмаған болса, email тексеру бетіне бағыттаймыз
        if request.user.is_authenticated and not request.user.userprofile.approved:
            return redirect('verify_email')  # Перенаправляем на страницу подтверждения
        return view_func(request, *args, **kwargs)
    return _wrapped_view
    


class CustomPasswordChangeView(PasswordChangeView):
    """Құпиясөзді өзгерту үшін кастомды көрініс"""
    template_name = 'password_reset/password_change_template.html'  # Кастомды шаблонға ауыстырыңыз
    success_url = reverse_lazy('profile')  # Құпиясөзді сәтті өзгерткеннен кейінгі URL мекенжайын көрсетіңіз

    def get(self, request, *args, **kwargs):
        # Қажет болса, қосымша әрекеттер
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Қажет болса, қосымша әрекеттер
        return super().post(request, *args, **kwargs)


class CustomPasswordResetView(PasswordResetView):
    """Құпиясөзді қалпына келтіруге арналған кастомды көрініс"""
    template_name = 'password_reset/password_reset_form_template.html'  # Құпиясөзді қалпына келтіру пішіні және хат үшін
    email_template_name = settings.PASSWORD_RESET_EMAIL_TEMPLATE  # Хат шаблонын орнату
    success_url = reverse_lazy('password_reset_done')  # Құпиясөзді қалпына келтіру сәтті болғаннан кейін бағыттайтын мекенжай

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['domain'] = self.request.get_host()  # Доменді контекстке қосамыз
        return context


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """Құпиясөзді қалпына келтіру процесі аяқталғаннан кейінгі бет"""
    template_name = 'password_reset/password_reset_complete.html'  # Құпиясөзді қалпына келтіру аяқталғаннан кейін бағыттайтын бет

    def get(self, request, *args, **kwargs):
        # Қажет болса, қосымша әрекеттер
        return super().get(request, *args, **kwargs)



class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Құпиясөзді қалпына келтіруге арналған кастомды көрініс - хабар жіберілген соң, керекті парақшаға сілтеме """
    template_name = 'password_reset/password_reset_done.html'  # Замените на ваш кастомный шаблон

    def get(self, request, *args, **kwargs):
        # Қажет болса, қосымша әрекеттер
        return super().get(request, *args, **kwargs)

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Құпиясөзді растау беті"""
    template_name = 'password_reset/password_reset_confirm_template.html'  # Құпиясөзді қалпына келтіруді растау беті
    success_url = reverse_lazy('password_reset_complete')  # Растағаннан кейін бағыттайтын бет

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = 'https' if self.request.is_secure() else 'http'  # Хаттама мен доменді контекстке қосу
        context['domain'] = self.request.get_host()
        return context

backend = 'django.contrib.auth.backends.ModelBackend'  # Замените на фактический аутентификационный бэкенд

class SetPasswordFormForLoggedInUserForm(SetPasswordForm):
    """
    Жүйеге кірген пайдаланушыларға арналған құпиясөз орнату формасы.
    """
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )

    new_password2 = forms.CharField(
        label="Подтверждение нового пароля",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password) # Құпиясөзді сақтаймыз
        if commit:
            self.user.save()
        return self.user

@method_decorator(check_approved, name='dispatch')  # Барлық сыныпқа декоратор қолдану
class SetPasswordViewForLoggedInUser(View):
    """
    Жүйеге кірген пайдаланушыларға арналған құпиясөз орнату беті.
    """
    template_name = 'password_reset/set_password_template.html'  # Кастомды шаблонға ауыстырыңыз

    def get(self, request):
        user = request.user

        # Пайдаланушыда құпиясөз жоқтығын тексереміз
        if user.has_usable_password():
            return redirect('password_change_page')  # Құпиясөзді өзгерту бетіне бағыттау

        form = SetPasswordFormForLoggedInUserForm(user=user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = SetPasswordFormForLoggedInUserForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # Құпиясөз өзгерткеннен кейін пайдаланушыны қайтадан жүйеге енгіземіз
            additional_login(request, request.user, backend=backend)
            return redirect('profile')  # Пайдаланушыны профиль бетіне бағыттау
        return render(request, self.template_name, {'form': form})

@method_decorator(check_approved, name='dispatch')  # Барлық сыныпқа декоратор қолдану
class UnSetPasswordViewForLoggedInUser(View):  # Тек тестілеу үшін. Дамуда пайдаланбаңыз
    """
    Жүйеге кірген пайдаланушыға құпиясөзді бос орнату беті.
    """
    template_name = 'password_reset/set_password_template.html'  # Кастомды шаблонға ауыстырыңыз

    def get(self, request):
        user = request.user

        # Пайдаланушының құпиясөзі жоқтығын тексеру
        if not user.has_usable_password():
            return redirect('set_empty_password')  # Бос құпиясөз орнату бетіне бағыттау

        if user.has_usable_password():
            user.set_unusable_password()  # Пайдаланушы құпиясөзін пайдаланбайтын етіп орнату
            user.save()
            additional_login(request, request.user, backend=backend)
        return redirect('profile')  # Пайдаланушыны профиль бетіне бағыттау




class RegisterView(View):
    """
    Тіркелу беті.
    """
    template_name = 'registration/register.html'
    error_template_name = 'register_user_ntuser_phone_already_exists_error.html'

    def get(self, request, template_name=None):
        if template_name:
            self.template_name = template_name
        form = CustomUserCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, template_name=None):
        if template_name:
            self.template_name = template_name
        error = "Error: "  # Қате туралы хабарлама
        with transaction.atomic():  # Барлық операцияларды бір транзакцияға орау
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                phone = form.cleaned_data.get('phone')
                user.save()

                # Пайдаланушының телефон нөмірін сақтаймыз
                user_phone = UserPhone(user=user, phone=phone)
                user_phone.save()

                # Пайдаланушының ID-ін сессияға сақтаймыз
                request.session['pending_user_id'] = user.id

                # Бір реттік пароль жіберу функциясын қолдану
                send_otp_email(user)

                # Электрондық поштаны растау бетіне бағыттау
                return redirect('verify_email')
            else:
                print(f"form.errors: {form.errors}")  # Пішін қателері туралы ақпарат
                error += f"{form.errors}"
                return render(request, self.error_template_name, {"error": error})



def generate_otp():
    """
    6 таңбалы бір реттік құпиясөз жасау.
    """
    return str(random.randint(100000, 999999))


def send_otp_email(user):
    """
    Пайдаланушының электрондық поштасына бір реттік құпиясөз жіберу.
    """
    otp_code = generate_otp()

    # OTP кодын базаға сақтаймыз
    OneTimePassword.objects.create(user=user, confirmation_code=otp_code)
    
    # Электрондық поштаға жібереміз
    subject = 'Подтверждение почты'  # Хат тақырыбы
    message = f'Ваш одноразовый пароль: {otp_code}.'  # Хат мәтіні
    from_email = settings.EMAIL_HOST_USER  # Жіберушінің электрондық поштасы
    recipient_list = [user.email]  # Қабылдаушы

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )


def login(request):
    """
    Негізгі логин функциясы.
    """
    try:
        user = request.user
        if user:
            # Пайдаланушы профилінің расталғанын тексеру
            if user.user_profile.is_approved:
                return redirect('profile')
            else:
                return redirect('verify_email')
    except Exception:
        pass
    return redirect('newlogin')


def send_one_time_password_to_email(request):
    """
    Пайдаланушының электрондық поштасына бір реттік пароль жіберу.
    """
    if not request.method == 'POST':
        return JsonResponse({'message': 'Неправильный метод запроса!'})  # Сұрау әдісі дұрыс емес

    email = request.POST.get('email')  # Электрондық пошта адресін аламыз

    # Аутентификацияланған пайдаланушыны тексереміз немесе сессиядан ID аламыз
    user = request.user if request.user.is_authenticated else None

    user_id = request.session.get('pending_user_id')
    if not user:
        if not user_id:
            messages.error(request, 'Вы не зарегистрированы или сессия истекла.')  # Қате хабарламасы
            print(f'no user_id in request.session')  # Сессияда пайдаланушының ID-і жоқ
            return JsonResponse({'error': 'no user_id in request.session.'}, status=400)
            
    if not user:
        try:
            user = User.objects.get(id=user_id)  # Пайдаланушыны ID арқылы аламыз
        except User.DoesNotExist:
            return JsonResponse({'error': 'Пользователь не найден. Попробуйте зарегистрироваться заново.'}, status=400)

    # Бір реттік құпиясөзді жасау
    otp_code = generate_otp()

    # Пайдаланушыға қатысты OTP базада сақталады
    OneTimePassword.objects.create(user=user, confirmation_code=otp_code)

    # Электрондық поштаға кодты жібереміз
    send_mail(
        'Ваш одноразовый пароль (OTP)',  # Хат тақырыбы
        f'Ваш одноразовый пароль: {otp_code}',  # Хат мәтіні
        settings.EMAIL_HOST_USER,  # Жіберушінің электрондық поштасы
        [email],  # Қабылдаушының электрондық поштасы
        fail_silently=False,
    )

    # Жауап қайтарамыз
    return JsonResponse({'message': 'Код отправлен на почту'})
    

def logout_view(request):
    """
    Жүйеден шығу функциясы.
    """
    logout(request)  # Пайдаланушыны жүйеден шығарамыз
    return redirect('newlogin')  # Логин бетіне қайта бағыттау


class VerifyEmailView(View):
    """
    Электрондық поштаны растау беті.
    """
    template_name = 'registration/verify_email.html'

    def get(self, request):
        # Сессиядан пайдаланушының ID-ін аламыз
        user_id = request.session.get('pending_user_id')
        if not request.user.is_authenticated:
            if not user_id:
                messages.error(request, 'Вы не зарегистрированы или сессия истекла.')  # Қате хабарламасы
                print(f'not request.user.is_authenticated and not user_id')  # Тіркелген пайдаланушы жоқ
                return redirect('newlogin')  # Тіркелу бетіне бағыттау
                
        # Пайдаланушыны ID арқылы аламыз
        if not request.user.is_authenticated:
            user = User.objects.get(id=user_id)
        else:
            user = request.user

        # Пайдаланушының электрондық поштасы расталғанын тексереміз
        if hasattr(user, 'userprofile') and user.userprofile.approved:
            messages.info(request, 'Ваша почта уже подтверждена.')  # Хабарлама
            return redirect('profile')  # Профиль бетіне бағыттау

        form = EmailVerificationForm()  # Электрондық пошта растау формасы
        return render(request, self.template_name, {'form': form})


    def post(self, request):
        form = EmailVerificationForm(request.POST)  # Растауды тексеру формасы
        pending_user_id = request.session.get('pending_user_id')  # Сессиядан ID аламыз
        print(f"request.session pending_user_id: {pending_user_id}")  # Сессия туралы ақпарат
        print(f"request.POST: {request.POST}")  # Пайдаланушының енгізген деректері
        if not request.user.is_authenticated:
            if not pending_user_id:
                messages.error(request, 'Вы не зарегистрированы или сессия истекла.')  # Қате хабарламасы
                return redirect('newlogin')  # Тіркелу бетіне бағыттау
            try:
                user = User.objects.get(id=pending_user_id)
            except:
                messages.error(request, 'Нет такого пользователя.')  # Қате пайдаланушы туралы
                print('Нет такого пользователя.')  # Қате туралы басып шығару
                return redirect('newlogin')  # Тіркелу бетіне бағыттау
        else:
            user = request.user

        if form.is_valid():
            otp_code = form.cleaned_data.get('otp_code')  # Пайдаланушы енгізген OTP кодын аламыз

            try:
                # Пайдаланушыға қатысты OTP кодты тексереміз
                otp_entry = OneTimePassword.objects.filter(user=user, confirmation_code=otp_code).order_by('-created_at').first()
                if otp_entry and otp_entry.is_valid():
                    # Егер код жарамды болса, пайдаланушыны растаймыз
                    user.userprofile.approved = True
                    user.userprofile.save()
                    otp_entry.delete()  # Расталған кодты жоямыз
                    OneTimePassword.delete_expired_passwords()  # Ескірген кодтарды жоямыз
                    messages.success(request, 'Ваша почта подтверждена.')  # Растау хабарламасы
                    print(request, 'Ваша почта подтверждена.')  # Логқа басып шығару
                    if 'pending_user_id' in request.session:    
                        del request.session['pending_user_id']  # Сессиядан ID-ді өшіреміз
                    return redirect('profile')  # Профиль бетіне бағыттау
                else:
                    form.add_error(None, 'Неверный или просроченный код.')  # Қате хабарламасы
            except OneTimePassword.DoesNotExist:
                form.add_error(None, 'Код подтверждения не найден.')  # Қате туралы басып шығару

        return render(request, self.template_name, {'form': form})  # Қате болған жағдайда бетті қайтару



class MyLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('profile')

    # POST сұраныстарына шектеу қолдану
    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=False))  # Әрбір IP үшін минутына 5 сұраныс. Бұғатталмайды, бірақ хабарлама береді
    def post(self, request, *args, **kwargs):
        if getattr(request, 'limited', False):  # Егер шектеу қолданылса

            error_message = "Слишком много попыток. Попробуйте через минуту."
            messages.error(request, error_message)
            print(f"post redirect")
            return redirect(f"{reverse('newlogin')}?error={error_message}")

        form = self.get_form()

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(self.request, username=username, password=password)

            if user is not None and user.is_active:
                # Пайдаланушыда екінші фактор аутентификациясы бапталғанын тексереміз
                if hasattr(user, 'authsecondfactor') and user.authsecondfactor.active:
                    # Екінші фактордың түрін аламыз
                    second_factor_type = user.authsecondfactor.second_factor

                    if second_factor_type == 'OTP':
                        # Бір реттік пароль (OTP) жасалып, email-ға жіберіледі
                        send_otp_email(user)
                        # Екінші факторлы аутентификация үшін пайдаланушыны сессияға сақтаймыз
                        self.request.session['two_factor_user_id'] = user.id
                        return redirect('two_factor_auth')
                    
                    elif second_factor_type == 'Quiz':
                        # Сауалнамаға жауап беру бетіне бағыттаймыз
                        self.request.session['two_factor_user_id'] = user.id
                        return redirect('two_factor_auth')

                    elif second_factor_type == 'Test':
                        # Тест бетіне бағыттаймыз
                        self.request.session['two_factor_user_id'] = user.id
                        return redirect('two_factor_auth')

                    else:
                        # Екінші фактордың түрі белгісіз болған жағдайда қате қайтарамыз
                        form.add_error(None, 'Белгісіз екі факторлы аутентификация түрі.')
                        return self.form_invalid(form)

                else:
                    # Егер екінші фактор белсенді болмаса, пайдаланушыны бірден авторизациялаймыз
                    self.request.session['pending_user_id'] = user.id
                    additional_login(self.request, user)
                    return redirect(self.success_url)

            else:
                return self.form_invalid(form)

        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.request.GET.get('username')  # Логин бетіне алдын ала толтыру үшін пайдаланушы аты
        error = self.request.GET.get('error')  # Қате туралы хабарлама
        if username:
            context['username'] = username
        if error:
            context['error'] = error
        if 'login_error' in self.request.session:
            context['error'] = self.request.session.pop('login_error')  # Қате хабарламасын көрсету
        context['error_messages'] = messages.get_messages(self.request)  # Барлық хабарламаларды қосу
        return context

        # error_message = self.request.GET.get('login_error')
        # allowed_messages = [
        #     "Неправильный логин или пароль",
        #     "Слишком много попыток. Попробуйте через минуту.",
        #     "Ваш аккаунт заблокирован"
        # ]
        # if error_message not in allowed_messages:
        #     error_message = "Ошибка"
        # context['login_error'] = error_message



class TwoFactorAuthView(FormView):
    """
    Екінші факторлы аутентификация көрінісі.
    """
    template_name = 'alter_authentication/two_factor_auth/two_factor_auth.html'
    form_class = TwoFactorAuthForm
    success_url = reverse_lazy('profile')

    def get(self, request, *args, **kwargs):
        # Сессиядан пайдаланушының ID-сін аламыз
        user_id = self.request.session.get('two_factor_user_id')
        print(f"two_factor_user_id: {user_id}")  # Логқа жазу
        if not user_id:
            messages.error(request, 'Пожалуйста, войдите заново для подтверждения.')  # Қате хабарламасы
            return redirect('newlogin')

        try:
            user = User.objects.get(id=user_id)  # Пайдаланушыны аламыз
            auth_second_factor = user.authsecondfactor  # Екінші факторды аламыз
        except (User.DoesNotExist, AuthSecondFactor.DoesNotExist):
            print(f"Проблема с вашей аутентификацией. Попробуйте заново")  # Қате туралы хабарлама
            messages.error(request, 'Проблема с вашей аутентификацией. Попробуйте заново.')
            return redirect('newlogin')

        context = self.get_context_data()
        if user.email:
            context['user_email'] = user.email  # Пайдаланушының электрондық поштасы
            print(f"user_email: {user.email}")  # Логқа жазу
        if auth_second_factor:
            context['auth_second_factor'] = auth_second_factor  # Екінші факторды контекстке қосамыз
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Кіретін POST сұранысты логтаймыз
        print(f"POST data received: {request.POST}")

        # POST сұраныстан мәліметтерді аламыз
        user_data = request.POST.get('user_data')

        # Сессиядан пайдаланушының ID-сін аламыз
        user_id = self.request.session.get('two_factor_user_id')
        if not user_id:
            # Егер пайдаланушының ID-сі сессияда жоқ болса, логин бетіне бағыттаймыз
            messages.error(self.request, 'Пожалуйста, войдите заново для подтверждения.')
            print(f"User ID not found in session. Redirecting to login.")
            return redirect('newlogin')

        # Пайдаланушыны ID бойынша аламыз
        try:
            user = User.objects.get(id=user_id)
            print(f"User found: {user.username} (ID: {user_id})")
        except User.DoesNotExist:
            messages.error(self.request, 'Пользователь не найден. Пожалуйста, зарегистрируйтесь заново.')
            print(f"User with ID {user_id} not found. Redirecting to register.")
            return redirect('register')

        # Екінші фактор түрін анықтап, сәйкесінше тексеру функциясын шақырамыз
        second_factor_type = user.authsecondfactor.second_factor
        print(f"Second factor type: {second_factor_type}")

        if second_factor_type == 'OTP':
            if self.validate_otp(user, user_data):
                print("OTP validation successful.")
                return self.complete_authentication(user)
            else:
                print("OTP validation failed.")
        elif second_factor_type == 'Quiz':
            if self.validate_quiz(user, user_data):
                print("Quiz validation successful.")
                return self.complete_authentication(user)
            else:
                print("Quiz validation failed.")
        elif second_factor_type == 'Test':
            if self.validate_test(user, user_data):
                print("Test validation successful.")
                return self.complete_authentication(user)
            else:
                print("Test validation failed.")

        # Егер тексеру сәтсіз аяқталса, қате хабарламасын қосамыз және пайдаланушыны қайта бағыттаймыз
        messages.error(self.request, 'Екінші фактордың қате тіркесі.')
        # print("Second factor validation failed. Redirecting back to two_factor_auth.")
        return redirect('two_factor_auth')
    

    def hash_value(self, value):
        """
        Берілген мәнді SHA-256 алгоритмімен хэштеу.
        """
        json_value = json.dumps(value, separators=(',', ':'))
        print(f"initial value (JSON): {json_value}")  # JSON мәнін дұрыс көрсету
        return hashlib.sha256(json_value.encode('utf-8')).hexdigest()


    def validate_otp(self, user, otp_code):
        """
        OTP кодын тексеру.
        """
        return_val = False
        OneTimePassword.delete_expired_passwords()  # Ескірген OTP кодтарын жою

        otp_entry = OneTimePassword.objects.filter(user=user).order_by('-created_at').first()
        print(f"Начало проверки OTP для пользователя {user} с кодом {otp_code}: {otp_entry}")  # OTP тексеру басталды
        print(f"otp_code {otp_code}: confirmation_code {otp_entry.confirmation_code}")  # OTP деректерін тексеру
        if otp_entry is not None and otp_entry.is_valid() and f'{otp_code}' == f'{otp_entry.confirmation_code}':
            print(f"Проверка пройдена. Валидный OTP")  # Тексеру сәтті өтті
            otp_entry.delete()  # Пайдаланылған OTP кодын жою
            return_val = True
        else:
            print(f"Проверка не пройдена. НеВалидный OTP:")  # OTP жарамсыз
            return_val = False
        return return_val


    def validate_quiz(self, user, user_answer):
        """
        Сұрақ жауабын тексеру.
        """
        try:
            # Пайдаланушының passvalue мәнінен деректерді жүктеу
            quiz_data = json.loads(user.authsecondfactor.passvalue)
            saved_hashed_answer = quiz_data.get('answer')  # Сақталған дұрыс жауап (хэш түрінде)

            # Пайдаланушы берген жауапты хэштеу
            hashed_user_answer = self.hash_value(user_answer.strip().lower())
            print(f"Expected hash: {saved_hashed_answer}")  # Күтілген хэш
            print(f"User-provided hash: {hashed_user_answer}")  # Пайдаланушының берген хэші

            return hashed_user_answer == saved_hashed_answer  # Екі хэшті салыстыру
        except (json.JSONDecodeError, AttributeError, KeyError) as e:
            print(f"Error during quiz validation: {e}")  # Викторина тексеруіндегі қате
            return False


    def validate_test(self, user, test_result):
        """
        Тест нәтижесін тексеру.
        """
        try:
            # Пайдаланушының тест параметрлерін алу
            test_params = UserSecondAuthenticationTestParams.objects.get(user=user)

            # Сақталған деректерді жүктеу
            saved_data = test_params.value_chain  # Бұл value_chain, test_type және obstaclesList бар дикт

            # Сақталған қозғалыстар тізбегінің хэшін алу
            saved_hash = saved_data.get('value_chain', '')  # Тек хэш түрінде сақталған value_chain

            # Пайдаланушы берген тест нәтижесін хэштеу
            received_hash = self.hash_value(json.loads(test_result))  # Пайдаланушының берген деректерін хэштеу

            # Логтарға жазу
            print(f"validate_test test_result: {test_result}")  # Пайдаланушының берген тест нәтижесі
            print(f"initial value (JSON): {test_result}")  # JSON түріндегі тест нәтижесі
            print(f"Сохраненный хэш: {saved_hash}")  # Сақталған хэш
            print(f"Полученный хэш: {received_hash}")  # Пайдаланушы берген хэш

            # Екі хэшті салыстыру
            if saved_hash == received_hash:
                return True
            return False
        except UserSecondAuthenticationTestParams.DoesNotExist:
            print("Ошибка: Параметры теста для пользователя не найдены.")  # Тест параметрлері табылмады
            return False
        except Exception as e:
            print(f"Ошибка при проверке теста: {e}")  # Тексеру кезінде қате
            return False


    def complete_authentication(self, user):
        """
        Аутентификацияны аяқтау функциясы.
        """
        additional_login(self.request, user)  # Пайдаланушыны жүйеге кіргізу
        del self.request.session['two_factor_user_id']  # Сессиядан пайдаланушының ID-сін жою
        return redirect(self.success_url)  # Пайдаланушыны сәтті бетке бағыттау



# class UserPhoneVerificationView(FormView):
#     template_name = 'phone_verification.html'
#     form_class = PhoneVerificationForm
#     success_url = reverse_lazy('profile')

#     def form_valid(self, form):
#         phone_number = form.cleaned_data.get('phone_number')
#         user = self.request.user
#         # Отправляем OTP для подтверждения телефона
#         send_otp_sms(user, phone_number)
#         return super().form_valid(form)

    

@method_decorator(check_approved, name='dispatch')  # Барлық сыныпқа декоратор қолдану
class Profile(View):
    """
    Профиль беті.
    """
    me = None
    template_name = 'alter_authentication/profile/profile_template.html'

    def hash_value(self, value):
        """
        Қозғалыстар тізбегін SHA-256 алгоритмімен хэштеу.
        """
        json_value = json.dumps(value, separators=(',', ':'))
        print(f"initial value (JSON): {json_value}")  # JSON мәнін дұрыс көрсету
        return hashlib.sha256(json_value.encode('utf-8')).hexdigest()

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        me = request.user  # Пайдаланушыны сұраныстан аламыз
        try:
            auth_second_factor = AuthSecondFactor.objects.get(user=me)  # Екінші факторды аламыз

        except AuthSecondFactor.DoesNotExist:
            auth_second_factor = None
            auth_second_factor_data = None

        context = {
            'me': me,  # Пайдаланушы туралы мәліметтерді контекстке қосамыз
            'auth_second_factor': auth_second_factor,  # Екінші фактор туралы мәліметтер
        }
        if auth_second_factor:
            if auth_second_factor.second_factor == 'Test':
                auth_second_factor_data = UserSecondAuthenticationTestParams.objects.filter(user=me, default=True).last()
                if auth_second_factor_data:
                    context['auth_second_factor_data'] = auth_second_factor_data  # Екінші фактор туралы мәліметтерді контекстке қосамыз

        print(f"context: {context}")  # Логқа контекст деректерін басып шығару
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        purpose = request.POST.get('purpose')  # Сұраудың мақсатын аламыз
        print(f"profile settings POST: {request.POST}")  # Сұрау деректерін логқа жазу

        if purpose == 'user_profile':
            try:
                me = request.user
                me.first_name = request.POST.get('first_name', me.first_name)  # Пайдаланушының аты
                me.email = request.POST.get('email', me.email)  # Электрондық пошта
                me.save()
                return JsonResponse({'status': 'success', 'message': 'Профиль сәтті жаңартылды!'})  # Жаңарту хабарламасы
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Профиль жаңарту қатесі: {str(e)}'}, status=400)

        elif purpose == 'second_factor':
            try:
                second_factor_method = request.POST.get('second_factor_method')  # Екінші фактор әдісін аламыз
                auth_factor, created = AuthSecondFactor.objects.get_or_create(user=request.user)

                if second_factor_method == 'OTP':
                    auth_factor.second_factor = 'OTP'
                    auth_factor.passvalue = ''
                    auth_factor.active = True
                    auth_factor.save()
                    return JsonResponse({'status': 'success', 'message': 'OTP әдісі сәтті бапталды!'})

                elif second_factor_method == 'Quiz':
                    question = request.POST.get('quizQuestion')  # Викторина сұрағы
                    answer = request.POST.get('quizAnswer')  # Викторина жауабы
                    quiz_data = {'question': question, 'answer': self.hash_value(answer.strip().lower())}
                    auth_factor.second_factor = 'Quiz'
                    auth_factor.passvalue = json.dumps(quiz_data)  # Деректерді JSON ретінде сақтаймыз
                    auth_factor.active = True
                    auth_factor.save()
                    return JsonResponse({'status': 'success', 'message': 'Quiz әдісі сәтті бапталды!'})

                elif second_factor_method == 'Test':
                    settings_data = request.POST.get('settings_data')  # Тест баптау деректері
                    if settings_data:
                        settings_json = json.loads(settings_data)
                        print(f"settings_json: {settings_json}")  # Логқа жазу
                        value_chain = settings_json.get('value_chain', [])
                        hashed_value_chain = self.hash_value(value_chain)

                        auth_factor.second_factor = 'Test'
                        auth_factor.passvalue = ''
                        auth_factor.active = True
                        auth_factor.save()
                        test_params, created = UserSecondAuthenticationTestParams.objects.get_or_create(
                            user=request.user,
                            defaults={
                                'value_chain': {
                                    'value_chain': hashed_value_chain,
                                    'test_type': settings_json.get('test_type', 'special_test'),
                                    'obstaclesList': settings_json.get('obstaclesList', []),
                                },
                                'default': True,
                            }
                        )

                        if not created:
                            test_params.default = True
                            test_params.value_chain = {
                                'value_chain': hashed_value_chain,
                                'test_type': settings_json.get('test_type', 'special_test'),
                                'obstaclesList': settings_json.get('obstaclesList', []),
                            }
                            test_params.save()

                        return JsonResponse({'status': 'success', 'message': 'Test әдісі сәтті бапталды!'})
                    else:
                        return JsonResponse({'status': 'error', 'message': 'Test үшін деректер дұрыс емес.'}, status=400)

                else:
                    return JsonResponse({'status': 'error', 'message': 'Белгісіз екінші фактор әдісі.'}, status=400)
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Екінші фактор баптау қатесі: {str(e)}'}, status=400)


        elif purpose == 'disable_second_factor':
            try:
                auth_factor = AuthSecondFactor.objects.get(user=request.user)
                auth_factor.active = False
                auth_factor.save()
                return JsonResponse({'status': 'success', 'message': 'Екі факторлы аутентификация сәтті өшірілді!'})
            except AuthSecondFactor.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Екі факторлы аутентификация бапталмаған.'}, status=400)
            
        elif purpose == 'password_change':
            print(f"Received current_password: {request.POST}")  # Құпиясөз сұрау деректері
            old_password = request.POST.get('old_password')  # Ескі құпиясөз
            new_password = request.POST.get('new_password')  # Жаңа құпиясөз

            user = request.user
            
            if not user.check_password(old_password):  # Құпиясөзді тексеру
                print(f"'status': 'error', 'message': 'Неправильный текущий пароль'")  # Қате хабарламасы
                return JsonResponse({'status': 'error', 'message': 'Неправильный текущий пароль.'}, status=400)
            
            try:
                validate_password(new_password, user=user)  # Жаңа құпиясөзді тексеру
            except ValidationError as e:
                print(f"'status': 'error', 'message': {e.messages[0]}")  # Қате хабарламасы
                return JsonResponse({'status': 'error', 'message': e.messages[0]}, status=400)
            
            user.set_password(new_password)  # Жаңа құпиясөзді сақтау
            user.save()
            print(f"'status': 'success', 'message': 'Пароль успешно изменён.'")  # Сәтті хабарлама
            return JsonResponse({'status': 'success', 'message': 'Пароль успешно изменён.'})

        print(f"'status': 'error', 'message': 'Некорректное действие.'")  # Дұрыс емес әрекет туралы хабарлама
        return JsonResponse({'status': 'error', 'message': 'Некорректное действие.'}, status=400)






