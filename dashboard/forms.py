from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import User

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
            'required': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль',
            'required': True,
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email'
        self.fields['password'].label = 'Пароль'

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
                if user.is_account_locked():
                    raise forms.ValidationError(
                        'Аккаунт заблокирован из-за множественных неудачных попыток входа. Попробуйте позже.'
                    )
                
                self.user_cache = authenticate(
                    self.request, 
                    username=email, 
                    password=password
                )
                
                if self.user_cache is None:
                    user.increment_failed_attempts()
                    raise forms.ValidationError('Неверный email или пароль.')
                else:
                    user.reset_failed_attempts()
                    
            except User.DoesNotExist:
                raise forms.ValidationError('Неверный email или пароль.')

        return self.cleaned_data 