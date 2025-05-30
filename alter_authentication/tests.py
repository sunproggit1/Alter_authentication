from django.test import TestCase
from django.test.utils import override_settings

from django.urls import reverse
from django.contrib.auth.models import User

class AuthenticationTest(TestCase):
    def setUp(self):
        # Тестке арналған пайдаланушыны жасау
        user = User.objects.create_user(username='testuser')
        user.set_password('correctpassword')  # Парольді дұрыс хэштеу
        user.save()
        self.user = user
        self.login_url = reverse('newlogin')  # Сілтемені динамикалық түрде алу
        print(f"[SETUP] Тестке арналған пайдаланушы жасалды: {self.user.username}")

    def test_login_success(self):
        print("1 [TEST] Логин сәтті тексеру...")
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'correctpassword'
        })
        print(f"1 [DEBUG] Жауап коды: {response}")
        print(f"1 [DEBUG] Жауап коды: {response.status_code}")
        self.assertEqual(response.status_code, 200, msg="Логин сәтті болуы керек.")

    def test_login_fail_wrong_password(self):
        print("2 [TEST] Қате парольмен логин тексеру...")
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        print(f"2 [DEBUG] Жауап коды: {response}")
        print(f"2 [DEBUG] Жауап коды: {response.status_code}")
        self.assertNotEqual(response.status_code, 200, msg="Қате парольмен кіруге рұқсат етілмеуі керек.")
