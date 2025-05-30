from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from django.contrib.auth.forms import UserCreationForm ## новый импорт кастомной формы создания пользователя

import re


class OneTimePasswordForm(forms.Form):
    ## одноразовый пароль
    # phone = forms.IntegerField(label="Номер телефона")
    otp = forms.IntegerField(label="Код подтверждения",max_value=999999)


    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'

            
class CustomUserCreationForm(UserCreationForm):
    phone = forms.CharField(label='Телефон', max_length=20)
    email = forms.EmailField(label='Email', required=True)  # Делаем email обязательным

    def clean_phone(self):
        phone = self.cleaned_data['phone']

        # Проверяем, что номер телефона состоит только из цифр
        if not re.match(r'^\d+$', phone):
            raise forms.ValidationError('Номер телефона должен содержать только цифры.')

        return phone

    # def clean_email(self):
    #     email = self.cleaned_data.get('email')

    #     # Проверяем уникальность email
    #     if User.objects.filter(email=email).exists():
    #         raise forms.ValidationError('Этот email уже зарегистрирован.')

    #     return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['required'] = True
        self.fields['first_name'].widget.attrs['required'] = True
        self.fields['email'].widget.attrs['required'] = True  # Обязательно указываем как обязательное поле

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 
                  'phone'
                  ]
        labels = {
            'phone': 'Номер телефона',
            'email': 'Email'
        }
        widgets = {
            # 'phone': forms.NumberInput(attrs={'class':'form-control form-control-sm'}),
        }



class EmailVerificationForm(forms.Form):
    otp_code = forms.CharField(
        max_length=6,
        label='Введите одноразовый код',
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )


class TwoFactorAuthForm(forms.Form):
    user_data = forms.CharField(max_length=100)

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'
            self.fields[field].widget.attrs['autocomplete'] = 'off'
            