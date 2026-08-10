from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'postal_code']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '太郎', 'required': 'required'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '山田', 'required': 'required'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'example@example.com', 'required': 'required'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '090-1234-5678', 'required': 'required'}),
            'address': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '東京都渋谷区...', 'required': 'required'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '150-0002', 'required': 'required'}),
        }
