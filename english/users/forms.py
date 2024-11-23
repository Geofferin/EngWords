from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm

'''
    ТУТ МЫ ПРОСТО СОЗДАЕМ НУЖНЫЕ НАМ ФОРМЫ, КОТОРЫЕ ПОТОМ ИМПОРТИРУЕМ В views.py
'''

class LoginUserForm(AuthenticationForm):
    # Указываем 'class': 'form-input', чтобы в дальнейшем применить нужные нам стили для этого класса
    username = forms.CharField(label='Логин или email')#, widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль')#, widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = get_user_model()  # Возвращает текущую модель пользователя
        fields = ['username', 'password']


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput())

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        labels = {
            'email': 'E-mail',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }

    # проверка уникальности email
    def clean_email(self):
        email = self.cleaned_data['email']
        # Если email уже существует в базе
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с такой почтой уже зарегистрирован!')
        return email


class ProfileUserForm(forms.ModelForm):
    username = forms.CharField(label='Логин')#, widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.CharField(label='E-mail')#, widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Старый пароль")#, widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password1 = forms.CharField(label="Новый пароль")#, widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password2 = forms.CharField(label="Подтверждение пароля")#, widget=forms.PasswordInput(attrs={'class': 'form-input'}))
