from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from .models import Quest,User,Status  # Quest,User,Statusモデルをインポート
from .forms import QuestForm  # QuestFormをインポート
from django.conf import settings  # settings.pyからパスワードを取り込むために必要
# ChatGPT関連
from langchain.agents import Tool, initialize_agent, AgentType
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import requests #function callingを使うなら必要

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
    status = Status.objects.filter(user=user.user_id).order_by("category")  # 取得したユーザーを使ってステータスを取得
    return render(request, 'gamification/display_status.html', {'user': user, 'status': status})  # 取得したユーザーをテンプレートに渡す

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
    else:
        quest.status = '未受注'
        quest.save()
    return redirect('quest')  


    return redirect('quest')  

# テンプレートには「誰が」「何をしゃべった」だけを送ってる
# 裏で、セッションでJson形式で履歴保存
def gpt(request):
    api_key = ''
    messages = []
    message_list = []

    # 2回目以降(POSTでリクエスト時)の処理
    if request.method == 'POST':
        question = request.POST.get('question')  # 質問を取得
        api_key = request.POST.get('api_key')  # APIキーを取得
        # 会話のリセット用。「reset」に反応。ボタンとかの方がいいかも？
        if question=="reset":
            del request.session['messages']
        else:
            # API関連の処理
            base_url = "https://api.openai.iniad.org/api/v1"
            model = "gpt-4o-mini"
            temperature = 0.2 # 答えの精度。0~2で、0に近いほど毎回同じ答えが返ってきやすい。
            chat = ChatOpenAI(openai_api_key=api_key, openai_api_base=base_url, model_name=model, temperature=temperature)
        

            # もし、セッションに会話履歴があったらその続きから会話する処理
            if 'messages' in request.session:
                messages = request.session['messages']
                # JSONからHumanMessageとAIMessageオブジェクトに戻す
                messages = [
                    HumanMessage(content=msg['content']) if msg['role'] == 'human' else 
                    AIMessage(content=msg['content']) if msg['role'] == 'ai' else
                    SystemMessage(content=msg['content'])
                    for msg in messages
                ]
            else:
                messages = [
                    SystemMessage(content="あなたは日本語を英語に翻訳するアシスタントです。ユーザーの日本語を英語に翻訳してください。")
                ]
            

            messages.append(HumanMessage(content=question)) # 会話履歴(あれば)の最後に今回の質問を入れる
            result = chat(messages) # ここでGPTにアクセスして回答を得る
            messages.append(result) # 回答も履歴に入れる

            # HumanMessage、AIMessage、SystemMessageオブジェクトをJSON形式に適応するために辞書形式に変換
            messages_to_save = [
                {'role': 'human', 'content': msg.content} if isinstance(msg, HumanMessage) else 
                {'role': 'ai', 'content': msg.content} if isinstance(msg, AIMessage) else
                {'role': 'system', 'content': msg.content}
                for msg in messages
            ]
            # セッションに現時点での会話を保存
            request.session['messages'] = messages_to_save

            # メッセージのタイプを識別してコンテキストに渡すリストを作成
            for message in messages:
                message_list.append({
                    'type': type(message).__name__,
                    'content': message.content
                })

    context = {
        'api_key': api_key,
        'messages': message_list,  # 会話の履歴など
        'response_text': messages[-1].content if messages else "",  # ChatGPTの最新の応答
    }

    return render(request, "gamification/225-GPT.html", context)

# 汎用版GPTの回答出力
def get_gpt_response(api_key, order, user_message, temperature=0.2): # APIキー、命令、渡すテキスト、答えの精度(0~2で、0に近いほど毎回同じ答えが返ってきやすい。)
    base_url = "https://api.openai.iniad.org/api/v1"
    model = "gpt-4o-mini"
    chat = ChatOpenAI(openai_api_key=api_key, openai_api_base=base_url, model_name=model, temperature=temperature)

    # 渡す会話を初期化
    messages = [
        SystemMessage(content=order),
        HumanMessage(content=user_message)
    ]

    # 回答の生成
    result = chat(messages)

    return result.content  # AIの応答内容を返す

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
                HumanMessage(content='100文字で要約してください'),
                HumanMessage(content=content)
            ]

            result = chat.invoke(messages)  # 前述のchatインスタンスを使用
            # resultの構造
            summary = result.content if hasattr(result, 'content') else '要約の取得に失敗しました'
            return JsonResponse({'summary': summary})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

#chat = ChatOpenAI(openai_api_key=OPENAI_API_KEY, openai_api_base=OPENAI_API_BASE, model_name='gpt-4o-mini', temperature=2)

@csrf_exempt
def generate_difficult(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            content = data.get('content', '')

            # OpenAI APIを使用した要約処理
            messages = [
                HumanMessage(content='難易度を、1から5段階で答えてくださいあと、数字のみでお願いします'),
                HumanMessage(content=content)
            ]

            result = chat.invoke(messages)  # 前述のchatインスタンスを使用
            # resultの構造を確認した方が良い
            summary = result.content if hasattr(result, 'content') else '要約の取得に失敗しました'
            return JsonResponse({'summary': summary})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

