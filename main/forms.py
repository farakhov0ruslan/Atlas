from django import forms
from django.contrib.auth.forms import UserCreationForm

from routes.models import CustomUser


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = CustomUser
        fields = ['email'
                  '', 'password1', 'password2', 'username']

    def clean_username(self):
        # Просто возвращаем введённое значение без проверки уникальности
        return self.cleaned_data.get('username')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']  # Сохраняем email как идентификатор
        if commit:
            user.save()
        return user
