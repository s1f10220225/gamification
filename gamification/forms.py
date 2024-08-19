from django import forms
from .models import Quest

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