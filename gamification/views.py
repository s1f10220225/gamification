from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from .models import Quest, User, Status, Party, PartyBelonged, Category  # Quest, User, Status, Party, PartyBelonged, Categoryモデルをインポート
from .forms import QuestForm, SignUpForm, LoginForm, CareerForm   # Formをインポート
from django.conf import settings  # settings.pyからパスワードを取り込むために必要
from django.views import View
from django.urls import reverse, reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView
import re # 正規表現による検索を行うため必要

# ChatGPT関連
from langchain.agents import Tool, initialize_agent, AgentType
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import requests #function callingを使うなら必要

from django.shortcuts import render
from .models import User
from django.contrib.auth.decorators import login_required  # ログイン必須のデコレーターをインポート　# 認証済みユーザーのデコレータ

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

def career_to_status(request, user_id):
    if request.method == 'POST':
        form = CareerForm(request.POST) # フォームの受信
        insert_forms = request.POST['career'] # 受信したフォームからcareerを取り出す
        user = get_object_or_404(User, pk=user_id)  # IDを使ってユーザーを取得
        status = Category.objects.all().values_list("status_name").order_by("category_name").distinct() # ステータス一覧の取得(カテゴリーごとにソート)
        status_list = [] #後々使う処理のため存在するステータスを記録するリスト
        order = "これからとある人のキャリアを送ります。あなたはその人のキャリアからその人のステータスを作成してください。各ステータスは「'ステータス名:0から100の数値'」という形で表してください。存在するステータスは次の通りです。「"
        for s in status:
            order += s[0] + "、"
            status_list.append(s[0])
        order = order[:-1]
        order += "」、これらの中からステータスをいくつか選んで数値化してください。ステータス名とその値以外の物を出力しないでください。" # GPTに与える命令文
        api_key = user.gpt_key # apiキーの取得
        try:
            gpt_return = get_gpt_response(api_key, order, insert_forms, temperature=0.1) # APIを利用してGPTからの返答を得る
            match = re.finditer(r'([a-zA-Z]+):\s*([0-9]+)', gpt_return)  # 正規表現を用いて「スキル名:スキル値」を検索
            gpt_tuples = []
            for m in match:
                gpt_tuples.append(m.groups())  # 「（スキル名,スキル値）」のタプルをリストに保存
            status_name = []
            status_value = []
            for t in gpt_tuples:
                status_name.append(t[0])  # スキル名をリストに保存
                status_value.append(t[1])  # スキル値をリストに保存
            for s in status_list: #GPTの出力になかったステータスに0を代入する処理
                if s not in status_name:
                    status_name.append(s)
                    status_value.append(0)
            zip_status = zip(status_name, status_value)  # スキル名、スキル値をまとめてとれるリスト作成
        except: # エラーが起きた場合(主にAPIキーが違ったりする場合)
            gpt_return = "Error"
            zip_status = []
        try: #データベースに保存する処理
            for s_name, s_value in zip(status_name, status_value):
                u = user
                c = Category.objects.filter(status_name=s_name)[0]
                p = s_value
                try: #データベースに値が存在する場合
                    objects = Status.objects.filter(user=u, category=c)
                    obj = objects[0]
                    obj.parameter = p
                    obj.save()
                except: #データベースに値が存在しなかった場合
                    new = {'user':u, 'category':c, 'parameter':p}
                    obj = Status(**new)
                    obj.save()
            submit_status = "All submit succeeded"
        except: #途中で登録に失敗した場合
            submit_status = "Some submit failed"
        return render(request, 'gamification/career_to_status.html', {'user': user, 'form': form, 'gpt_return':gpt_return, 'status':zip_status, 'submit':submit_status})
    else:
        form = CareerForm()
        insert_forms = '初期値'
        user = get_object_or_404(User, pk=user_id)  # IDを使ってユーザーを取得
        return render(request, 'gamification/career_to_status.html', {'user': user, 'form': form, 'insert_forms':insert_forms, 'submit':"Not submitted"})  # 取得したユーザーをテンプレートに渡す

def password(request):
    return render(request, "gamification/259pass.html")  # この関数は必要ないかも

def password2(request):
    if request.method == 'POST':
        input_password = request.POST.get('password2')
        if input_password == settings.PASSWORD:
            return redirect('summary')
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




@login_required  # このデコレーターを使ってログインを必須にする
def summary(request):
    user_message = ''
    response = ''
    api_key = request.user.gpt_key  # ログインしているユーザーのgpt_keyを取得

    if request.method == 'POST':
        user_message = request.POST.get('user_message', '')

        if api_key:  # APIキーがログインユーザーから取得される場合のみ処理
            order = "文章の要約をお願い。要点をまとめるようにしてまた、難易度[AからG]とどのくらいの期間が必要かを書いてほしい"

            try:
                # get_gpt_response関数を呼び出し、api_keyを使用
                response = get_gpt_response(api_key, order, user_message, temperature=0.2)
            except Exception as e:
                response = f"エラーが発生しました: {str(e)}"

    return render(request, "gamification/259add_quest.html", {
        'user_message': user_message,
        'response': response,
        'api_key': api_key  # APIキーはユーザーからを利用
    })

def create_quest(request):
    if request.method == 'POST':
        form = QuestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('quest')  # 成功した場合のリダイレクト先を指定
    else:
        form = QuestForm()

    return render(request, 'gamification/create_quest.html', {'form': form})

def delete_quest(request, quest_id):
    
    quest = get_object_or_404(Quest, quest_id=quest_id) 

    if request.method == 'POST':
        quest.delete()  
        return HttpResponseRedirect(reverse('quest'))  

    return render(request, "gamification/259quest_list.html", {'quest': quest})

    
## ユーザー認証システム
class SignUp(CreateView):
    form_class = SignUpForm
    template_name = "gamification/signup.html" 
    success_url = reverse_lazy('signup_complete')

    def form_valid(self, form):
        name = form.cleaned_data['name']
        gpt_key = form.cleaned_data['gpt_key']
        password = form.cleaned_data['password1']  # ここでpassword1を取得

        # CustomUserManager経由でユーザーを作成
        user = User.objects.create_user(name=name, gpt_key=gpt_key, password=password)

        # ユーザーをログインさせる
        login(self.request, user) # 認証
        self.object = user
        return HttpResponseRedirect(self.get_success_url()) # リダイレクト

# サインアップ後の画面
def signup_complete(request):
    return render(request, 'gamification/signup_complete.html')

# ログイン時のフォーム表示(デフォルトだと社員番号がカラム名になるため)
class LoginView(LoginView):
    authentication_form = LoginForm
    template_name = 'gamification/login.html'


@login_required  # このデコレータを加えることでログイン必須にする
def user_profile(request):
    user = request.user  # 現在のログインユーザーを取得
    return render(request, 'gamification/user_profile.html', {'user': user})

def toppage(request):
    return render(request, "gamification/224toppage.html") 


def main_login(request):
    return render(request, "gamification/224login.html")