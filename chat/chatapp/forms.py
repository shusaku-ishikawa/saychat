from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import *
from django.core.exceptions import ValidationError


class LoginForm(AuthenticationForm):
    """ログインフォーム"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label  # placeholderにフィールドのラベルを入れる

class SignUpForm(UserCreationForm):
    """ユーザー登録用フォーム"""

    class Meta:
        model = User
        MONTHS = {
            1: '1', 2: '2', 3: '3', 4: '4',
            5: '5', 6: '6', 7: '7', 8: '8',
            9: '9', 10: '10', 11: '11', 12: '12'
        }
        widgets = {
            'birthday': forms.SelectDateWidget(years = range(2022, 1930, -1), months=MONTHS)
        }
        fields = ('email', 'name', 'furigana', 'birthday', 'address', 'phone', 'clinic_name', 'thumbnail')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label  # placeholderにフィールドのラベルを入れる

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        MONTHS = {
            1: '1', 2: '2', 3: '3', 4: '4',
            5: '5', 6: '6', 7: '7', 8: '8',
            9: '9', 10: '10', 11: '11', 12: '12'
        }
        widgets = {
            'birthday': forms.SelectDateWidget(years = range(2022, 1930, -1), months=MONTHS)
        }
        fields = ('email', 'name', 'furigana', 'birthday', 'address', 'phone', 'clinic_name', 'thumbnail')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label  # placeholderにフィールドのラベルを入れる