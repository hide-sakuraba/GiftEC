from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'example@example.com'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '太郎'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '山田'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'last_name', 'first_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ユーザー名'}),
        }
