from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm

from django.contrib.auth.models import User

class UserLoginForm(AuthenticationForm):
    """Форма для входа"""
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control mb-3', 'placeholder': 'Username', 'id': 'login-username'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password', 'id': 'login-pwd'}))

class UserEditForm(forms.ModelForm):
    """Форма для редактирования информации о пользователи"""
    email = forms.EmailField(
        label='Электронная почта аккаунта (не может быть изменена)', max_length=200, widget=forms.TextInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'email', 'id': 'form-email', 'readonly': 'readonly'}
        )
    )

    last_name = forms.CharField(
        label='Фамилия', max_length=50, widget=forms.TextInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'Фамилия', 'id': 'form-lastname'}
        )
    )

    first_name = forms.CharField(
        label='Имя', max_length=50, widget=forms.TextInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'Имя', 'id': 'form-firstname'}
        )
    )

    class Meta:
        model = User
        fields = ('email', 'last_name', 'first_name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['last_name'].required = True
        self.fields['first_name'].required = True
        self.fields['email'].required = True

class PwdResetForm(PasswordResetForm):
    """Форма для сброса пароля"""
    email = forms.EmailField(max_length=254, widget=forms.TextInput(
        attrs={'class': 'form-control mb-3', 'placeholder': 'Email', 'id': 'form-email'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email)
        if not user:
            raise forms.ValidationError(
                'К сожалению, мы не можем найти этот адрес электронной почты.'
            )
        return email

class PwdResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='New password', widget=forms.PasswordInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'New Password', 'id': 'form-newpassword1'}
        )
    )
    new_password2 = forms.CharField(
        label='Repeat Password', widget=forms.PasswordInput(
            attrs={'class': 'form-control mb-3', 'placeholder': 'New Paswword', 'id': 'form-newpassword2'}
        )
    )