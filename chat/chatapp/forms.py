from django import forms

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import *
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
        fields = ('email', 'name', 'furigana', 'birthday', 'address', 'phone', 'clinic_name', 'thumbnail', 'alert_freq')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label  # placeholderにフィールドのラベルを入れる
        self.fields['name'].widget.attrs['placeholder'] = "例) オプト　太郎"
        self.fields['furigana'].widget.attrs['placeholder'] = "例) オプト　タロウ"
        self.fields['email'].widget.attrs['placeholder'] = "パソコン、携帯どちらも可"
        self.fields['clinic_name'].widget.attrs['placeholder'] = "例) オプテック歯科医院"
        self.fields['address'].widget.attrs['placeholder'] = "例) 北海道札幌市厚別区厚別西２条3-7-15"
        self.fields['phone'].widget.attrs['placeholder'] = "固定電話、携帯どちらも可"
        self.fields['password1'].widget.attrs['placeholder'] = "8文字以上"
        self.fields['password2'].widget.attrs['placeholder'] = "8文字以上"
 
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
        fields = ('email', 'name', 'furigana', 'birthday', 'address', 'phone', 'clinic_name', 'thumbnail', 'alert_freq')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            
        self.fields['name'].widget.attrs['placeholder'] = "例) オプト　太郎"
        self.fields['furigana'].widget.attrs['placeholder'] = "例) オプト　タロウ"
        self.fields['email'].widget.attrs['placeholder'] = "パソコン、携帯どちらも可"
        self.fields['clinic_name'].widget.attrs['placeholder'] = "例) オプテック歯科医院"
        self.fields['address'].widget.attrs['placeholder'] = "例) 北海道札幌市厚別区厚別西２条3-7-15"
        self.fields['phone'].widget.attrs['placeholder'] = "固定電話、携帯どちらも可"

class MyPasswordChangeForm(PasswordChangeForm):
    """パスワード変更フォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label  # placeholderにフィールドのラベルを入れる

class MyPasswordResetForm(PasswordResetForm):
    """パスワード忘れたときのフォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label  # placeholderにフィールドのラベルを入れる


class MySetPasswordForm(SetPasswordForm):
    """パスワード再設定用フォーム(パスワード忘れて再設定)"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label  # placeholderにフィールドのラベルを入れる

