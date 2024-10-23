from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from .models import Quest,User,Status  # Quest,User,Statusモデルをインポート
from .forms import QuestForm  # QuestFormをインポート
from django.conf import settings  # settings.pyからパスワードを取り込むために必要

def top(request):
    return render(request, "gamification/top.html")

def quest(request):
    quests = Quest.objects.all()
    return render(request, "gamification/259quest_list.html", {'quests': quests})

def quest_detail(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    return render(request, "gamification/259quest_detail.html", {'quest': quest})

def add_quest(request):
    if request.method == 'POST':
        form = QuestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('quest')
    else:
        form = QuestForm()

    return render(request, "gamification/259add_quest.html", {'form': form})  # フォームをテンプレートに渡す

def display_status(request, user_id):
    user = get_object_or_404(User, pk=user_id)  # IDを使ってユーザーを取得
    status = Status.objects.filter(user=user.user_id)  # 取得したユーザーを使ってステータスを取得
    return render(request, 'gamification/display_status.html', {'user': user, 'status': status})  # 取得したユーザーをテンプレートに渡す

def password(request):
    return render(request, "gamification/259pass.html")  # この関数は必要ないかも

def password2(request):
    if request.method == 'POST':
        input_password = request.POST.get('password2')
        if input_password == settings.PASSWORD:
            return redirect('add_quest')
        else:
            return render(request, 'gamification/259pass.html', {'error': 'パスワードが正しくありません。'})
    return render(request, 'gamification/259pass.html')

def accept_quest(request, quest_id):
    quest = get_object_or_404(Quest, quest_id=quest_id)

    if quest.status == '未受注':
        quest.status = '受注'
        quest.save()

    return redirect('quest')  
