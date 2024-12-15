from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Quest, User

class QuestForm(forms.ModelForm):
    class Meta:
        model = Quest
        fields = ['party', 'requester', 'title', 'detail', 'difficulty', 'time']
        labels = {
            'party': 'パーティー',
            'requester': '依頼者',
            'title': 'クエストタイトル',
            'detail': 'クエストの詳細',
            'difficulty': '難易度',
            'time': '予想時間',
        }

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "name",
            "gpt_key",
        )

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='社員番号')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput)
