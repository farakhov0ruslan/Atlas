from django import forms
from django.contrib.auth.forms import UserCreationForm
from routes.models import CustomUser


class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(required=True, label="Имя пользователя")
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2"]  # Добавили username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["username"]  # Сохраняем имя пользователя
        user.email = self.cleaned_data["email"]  # Сохраняем email
        if commit:
            user.save()
        return user