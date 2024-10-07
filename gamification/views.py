from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from .models import Quest  # Questモデルをインポート
from .forms import QuestForm  # QuestFormをインポート
# ChatGPT関連
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import requests #function callingを使うなら必要

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


# テンプレートには「誰が」「何をしゃべった」だけを送ってる
# 裏で、セッションでJson形式で履歴保存
def gpt(request):
    api_key = ''
    messages = []
    message_list = []
    initialized = False

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
                initialized = True # 初回フラグを設定
            

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
