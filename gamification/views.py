from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from .models import Quest,User,Status  # Quest,User,Statusモデルをインポート
from .forms import QuestForm  # QuestFormをインポート

def top(request):
    return render(request, "gamification/top.html")

def quest(request):
    quests = Quest.objects.all()  # Questモデルから全てのクエストを取得
    return render(request, "gamification/259quest_list.html", {'quests': quests})  # コンテキストとしてquestsを渡す

def quest_detail(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)  # IDを使ってクエストを取得
    return render(request, "gamification/259quest_detail.html", {'quest': quest})  # 取得したクエストをテンプレートに渡す

def add_quest(request):
    if request.method == 'POST':
        form = QuestForm(request.POST)  # 修正
        if form.is_valid():
            form.save()
            return redirect('quest')  # 追加後にクエスト一覧にリダイレクト
    else:
        form = QuestForm()

    return render(request, "gamification/259add_quest.html", {'form': form})  # フォームをテンプレートに渡す

def display_status(request, user_id):
    user = get_object_or_404(User, pk=user_id)  # IDを使ってユーザーを取得
    status = get_object_or_404(Status, pk=user.user_id)  # 取得したユーザーを使ってステータスを取得
    return render(request, 'gamification/display_status.html', {'user': user, 'status': status})  # 取得したユーザーをテンプレートに渡す