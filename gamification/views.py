from django.shortcuts import render, redirect, get_object_or_404
from .models import Quest
from .forms import QuestForm
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

    return render(request, "gamification/259add_quest.html", {'form': form})

#def password(request):
#    return render(request, "gamification/259pass.html")  # この関数は必要ないかも

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
def delete_quest(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    quest.delete()
    return redirect('quest')  # 削除後のリダイレクト先を指定
#/////////////////
# views.py
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# OpenAI APIキーやベースURLの設定
OPENAI_API_KEY = ""  # 必要に応じてセキュアに管理してください
OPENAI_API_BASE = 'https://api.openai.iniad.org/api/v1'  # 正しいAPIベースURLに修正

# ChatOpenAIインスタンスを初期化
chat = ChatOpenAI(openai_api_key=OPENAI_API_KEY, openai_api_base=OPENAI_API_BASE, model_name='gpt-4o-mini', temperature=2)

@csrf_exempt
def generate_summary(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            content = data.get('content', '')

            # OpenAI APIを使用した要約処理
            messages = [
                HumanMessage(content='30文字で要約してください'),
                HumanMessage(content=content)
            ]

            result = chat(messages)  # 前述のchatインスタンスを使用
            # resultの構造を確認した方が良い
            summary = result.content if hasattr(result, 'content') else '要約の取得に失敗しました'
            return JsonResponse({'summary': summary})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)
