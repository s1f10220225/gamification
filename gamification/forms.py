from django import forms
from django.contrib.auth.forms import UserCreationForm
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