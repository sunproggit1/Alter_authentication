from django.shortcuts import redirect
from django.urls import reverse

class CheckApprovedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Проверяем, подтвержден ли пользователь
            if not request.user.userprofile.approved:
                # Исключаем страницы, которые должны быть доступны без подтверждения
                if request.path not in [reverse('verify_email'), reverse('logout')]:
                    return redirect('verify_email')  # Перенаправляем на страницу подтверждения
                
        response = self.get_response(request)
        return response
