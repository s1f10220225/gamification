from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from .models import Quest, User, Status, Party, PartyBelonged  # Quest, User, Status, Party, PartyBelongedモデルをインポート
from .forms import QuestForm  # QuestFormをインポート
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



def display_status(request, user_id):
    user = get_object_or_404(User, pk=user_id)  # IDを使ってユーザーを取得
    status = Status.objects.filter(user=user.user_id).order_by("category")  # 取得したユーザーを使ってステータスを取得
    return render(request, 'gamification/display_status.html', {'user': user, 'status': status})  # 取得したユーザーをテンプレートに渡す



def password2(request):
    if request.method == 'POST':
        input_password = request.POST.get('password2')
        if input_password == settings.PASSWORD:
            return redirect('sample_return2')
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

def get_gpt_response(api_key, order, user_message, temperature=0.2):
    # APIキー、命令、渡すテキスト、答えの精度(0~2で、0に近いほど毎回同じ答えが返ってきやすい。)
    base_url = 'https://api.openai.iniad.org/api/v1' # 正しいURLに修正
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




def combined_view(request):
    form = QuestForm()  # フォームインスタンスを最初に作成
    user_message = ''  
    api_key = ''  # APIキーを保持
    response = ''

    if request.method == 'POST':
        if 'quest_form' in request.POST:
            form = QuestForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('quest')

        elif 'api_key' in request.POST:
            api_key = request.POST.get('api_key', '')  # APIキーを保持
            order = "文章の要約をお願い。要点をまとめるようにしてまた、難易度[AからG]とどのくらいの期間が必要かを書いてほしい"
            user_message = request.POST.get('user_message', '')

            try:
                response = get_gpt_response(api_key, order, user_message, temperature=0.2)
            except Exception as e:
                response = f"エラーが発生しました: {str(e)}"

            return render(request, "gamification/259add_quest.html", {
                "response": response,
                'form': form,
                'user_message': user_message,
                'api_key': api_key  # APIキーをコンテキストに追加
            })

    return render(request, "gamification/259add_quest.html", {
        'form': form,
        'user_message': user_message,
        'response': response,
        'api_key': api_key  # APIキーも保持
    })


from django.shortcuts import render, redirect
from .forms import QuestForm

def create_quest(request):
    if request.method == 'POST':
        form = QuestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')  # 成功した場合のリダイレクト先を指定
    else:
        form = QuestForm()
    
    return render(request, 'gamification/create_quest.html', {'form': form})
