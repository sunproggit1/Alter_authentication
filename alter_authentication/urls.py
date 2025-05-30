from django.contrib import admin
from django.urls import path
from alter_authentication import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Басты бет
    path('', views.login, name="account_login"),  # Қонақтарға арналған басты бет
    path('newlogin/', views.MyLoginView.as_view(), name='newlogin'),  # Жаңа логин беті

    # Тіркеу және аутентификация
    path('accounts/register/', views.RegisterView.as_view(), name='register_view'),  # Пайдаланушыны тіркеу
    path('accounts/login/', auth_views.LoginView.as_view(), name='new_login_page'),  # Логин беті
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='new_logout_page'),  # Жүйеден шығу

    # Құпиясөзді қалпына келтіру және өзгерту
    path('accounts/password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),  # Құпиясөзді қалпына келтіру
    path('accounts/reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),  # Құпиясөзді растау
    path('accounts/password_reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),  # Қалпына келтіру сәтті аяқталғаны туралы бет
    path('accounts/reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),  # Қалпына келтіру аяқталған соңғы бет
    path('accounts/password_change/', views.CustomPasswordChangeView.as_view(), name='password_change_page'),  # Құпиясөзді өзгерту беті

    # Тестілеуге арналған маршруттар (өндірісте пайдалануға болмайды)
    path('accounts/set_password/', views.SetPasswordViewForLoggedInUser.as_view(), name='set_empty_password'),  # Жүйеге кірген пайдаланушы үшін құпиясөзді орнату
    path('accounts/unset_password/', views.UnSetPasswordViewForLoggedInUser.as_view(), name='unset_password'),  # Құпиясөзді өшіру

    # Бір реттік құпиясөз (OTP)
    path('send_one_time_password_to_email/', views.send_one_time_password_to_email, name="send_one_time_password_to_email"),  # Бір реттік құпиясөзді email арқылы жіберу

    # Екі факторлы аутентификация
    path('two-factor-auth/', views.TwoFactorAuthView.as_view(), name='two_factor_auth'),  # Екі факторлы аутентификация беті
    path('two-factor-auth/login/', views.TwoFactorAuthView.as_view(), name='two_factor_auth_login'),  # Екі факторлы аутентификация арқылы логин жасау

    # Пайдаланушы профилі
    path('profile/', views.Profile.as_view(), name="profile"),  # Пайдаланушы профилі беті
    path('profile/set_changes_for_profile/', views.Profile.as_view(), name="set_changes_for_profile"),  # Профиль параметрлерін өзгерту

    # Email растау
    path('verify_email/', views.VerifyEmailView.as_view(), name='verify_email'),  # Email-ді верификациялау

    # Басқа қызметтер
    path('get_csrf_token', views.get_csrf_token, name='get_csrf_token'),  # CSRF токенін алу
]
