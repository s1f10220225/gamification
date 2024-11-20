from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from .models import Quest, User, Status, Category, Party, PartyBelonged  # Quest, User, Status, Category, Party, PartyBelongedモデルをインポート
from .forms import QuestForm, CareerForm  # QuestForm,CareerFormをインポート
from django.conf import settings  # settings.pyからパスワードを取り込むために必要
from django.views import View
from django.urls import reverse

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

def career_to_status(request, user_id):
    if request.method == 'POST':
        form = CareerForm(request.POST) # フォームの受信
        insert_forms = request.POST['career'] # 受信したフォームからcareerを取り出す
        user = get_object_or_404(User, pk=user_id)  # IDを使ってユーザーを取得
        status = Category.objects.all().values_list("status_name").order_by("category_name").distinct() # ステータス一覧の取得(カテゴリーごとにソート)
        order = "これからとある人のキャリアを送ります。あなたはその人のキャリアからその人のステータスを作成してください。各ステータスは「'ステータス名:0から100の数値'」という形で表してください。存在するステータスは次の通りです。「"
        for s in status:
            order += s[0] + "、"
        order = order[:-1]
        order += "」、これらの中からステータスをいくつか選んで数値化してください。ステータス名とその値以外の物を出力しないでください。" # GPTに与える命令文
        api_key = user.gpt_key # apiキーの取得
        try:
            gpt_return = get_gpt_response(api_key, order, insert_forms, temperature=0.1) # APIを利用してGPTからの返答を得る
        except: # エラーが起きた場合(主にAPIキーが違ったりする場合)
            gpt_return = "Invalid key error"
        if form.is_valid():
            return render(request, 'gamification/career_to_status.html', {'user': user, 'form': form, 'gpt_return':gpt_return})
    else:
        form = CareerForm()
        insert_forms = '初期値'
        user = get_object_or_404(User, pk=user_id)  # IDを使ってユーザーを取得
        return render(request, 'gamification/career_to_status.html', {'user': user, 'form': form, 'insert_forms':insert_forms})  # 取得したユーザーをテンプレートに渡す

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


# パーティーの作成
class CreatePartyView(View):
    def get(self, request):
        return render(request, 'gamification/225_create_party.html')

    def post(self, request):
        party_name = request.POST.get('party_name')
        party = Party.objects.create(name=party_name)
        return redirect(reverse('party_detail', args=[party.party_id]))

class AddMemberView(View):
    def get(self, request, party_id):
        party = get_object_or_404(Party, pk=party_id)
        users = User.objects.all()
        return render(request, 'gamification/225_add_member.html', {'party': party, 'users': users})

    def post(self, request, party_id):
        party = get_object_or_404(Party, pk=party_id)
        user_id = request.POST.get('user_id')
        role = request.POST.get('role')
        user = get_object_or_404(User, pk=user_id)
        PartyBelonged.objects.create(party=party, user=user, role=role)
        return redirect(reverse('party_detail', args=[party.party_id]))

class RemoveMemberView(View):
    def post(self, request, party_id, user_id):
        party = get_object_or_404(Party, pk=party_id)
        PartyBelonged.objects.filter(party=party, user_id=user_id).delete()
        return redirect(reverse('party_detail', args=[party.party_id]))

class PartyDetailView(View):
    def get(self, request, party_id):
        party = get_object_or_404(Party, pk=party_id)
        members = PartyBelonged.objects.filter(party=party)
        context = {'party': party, 'members': members}
        return render(request, 'gamification/225_party_detail.html', context)


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
