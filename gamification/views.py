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
from django.http import JsonResponse
import json

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
    #return render(request, "gamification/259quest_list.html", {'quests': quests})
    return render(request, "gamification/259quest_list.html", {'quests': quests})


def quest_detail(request, quest_id):
    quest = get_object_or_404(Quest, pk=quest_id)
    return render(request, "gamification/259quest_detail.html", {'quest': quest})
    
@login_required
def display_status(request):
    user = request.user
    status = Status.objects.filter(user=user.user_id).order_by("category")  # 取得したユーザーを使ってステータスを取得
    return render(request, 'gamification/display_status.html', {'user': user, 'status': status})  # 取得したユーザーをテンプレートに渡す

@login_required
def career_to_status(request):
    if request.method == 'POST':
        form = CareerForm(request.POST) # フォームの受信
        insert_forms = request.POST['career'] # 受信したフォームからcareerを取り出す
        user = request.user
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
        user = request.user
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
@login_required
def party_dashboard(request):
    # パーティと、そのメンバーのUserクエリを1発で取得
    parties = Party.objects.prefetch_related('members__user')  # membersを通じてuserを間接的に取得 

    context = {
        'parties': parties,
    }
    return render(request, "gamification/party_dashboard.html", {"parties": parties})

@login_required
def create_party(request):
    """
    新しいパーティーを作成するビュー。
    """
    if request.method == "POST":
        party_name = request.POST.get("party_name")
        purpose = request.POST.get("purpose")

        # パーティー作成
        party = Party.objects.create(name=party_name)
        PartyBelonged.objects.create(party=party, user=request.user, role="リーダー")

        return redirect("party_detail", party_id=party.party_id)

    return render(request, "gamification/create_party.html")

@login_required
def party_detail(request, party_id):
    """
    パーティーの詳細を表示するビュー。
    """
    party = get_object_or_404(Party, pk=party_id)
    members = PartyBelonged.objects.filter(party=party)
    return render(request, "gamification/party_detail.html", {"party": party, "members": members})

@login_required
def optimize_party(request, party_id):
    """
    GPTを使用して、ユーザーが指定した目的に応じてパーティーを最適化するビュー。
    """
    party = get_object_or_404(Party, pk=party_id)
    current_members = PartyBelonged.objects.filter(party=party)
    all_users = User.objects.all()

    if request.method == "POST":
        # ユーザーが入力した目的を取得
        purpose = request.POST.get("purpose")

        # ChatGPTへの指示を準備
        user_data = [
            {
                "name": user.name,
                "job": user.statuses.first().category.category_name if user.statuses.exists() else "不明",
                "statuses": {
                    status.category.status_name: status.parameter
                    for status in user.statuses.all()
                },
            }
            for user in all_users
        ]
        api_key = request.user.gpt_key
        prompt = f"""
        パーティー「{party.name}」を次の目的に合った構成に最適化してください：
        目的: {purpose}

        現在登録可能な候補メンバーの情報は以下です：
        {user_data}

        出力フォーマット:
        [
            {{"name": "名前", "job": "ジョブ", "reason": "選定理由"}},
            ...
        ]
        """
        try:
            suggested_party = get_gpt_response(api_key, prompt, "", temperature=0.7)
            suggested_party = json.loads(suggested_party)  # JSON形式の応答をパース
        except json.JSONDecodeError:
            return render(request, "gamification/error.html", {"message": "GPTからの回答が正しくありませんでした。再試行してください。"})

        # 仮登録メンバーをパーティーに保存
        for member in suggested_party:
            user = User.objects.filter(name=member["name"]).first()
            if user and not PartyBelonged.objects.filter(party=party, user=user).exists():
                PartyBelonged.objects.create(party=party, user=user, role=member["job"])

        return render(request, "gamification/party_optimization.html", {
            "party": party,
            "purpose": purpose,
            "suggested_party": suggested_party,
        })

    return render(request, "gamification/party_optimize_input.html", {"party": party})


@login_required
def edit_party(request, party_id):
    """
    パーティーのメンバー編集を行うビュー。
    """
    party = get_object_or_404(Party, pk=party_id)

    # パーティーのメンバーを取得
    members = PartyBelonged.objects.filter(party=party)

    if not PartyBelonged.objects.filter(party=party, user=request.user, role="リーダー").exists():
        return JsonResponse({"error": "リーダーのみが編集可能です。"})

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add_member":
            # メンバーを追加
            user_id = request.POST.get("user_id")
            role = request.POST.get("role")
            user = get_object_or_404(User, pk=user_id)
            if not PartyBelonged.objects.filter(party=party, user=user).exists():
                PartyBelonged.objects.create(party=party, user=user, role=role)
            return JsonResponse({"message": f"{user.name} がパーティーに追加されました。"})

        elif action == "remove_member":
            # メンバーを削除
            user_id = request.POST.get("user_id")
            PartyBelonged.objects.filter(party=party, user_id=user_id).delete()
            return JsonResponse({"message": "メンバーが削除されました。"})

        elif action == "update_role":
            # ジョブ（役職）を変更
            user_id = request.POST.get("user_id")
            new_role = request.POST.get("new_role")
            member = PartyBelonged.objects.filter(party=party, user_id=user_id).first()
            if member:
                member.role = new_role
                member.save()
            return JsonResponse({"message": f"{member.user.name} の役職が {new_role} に変更されました。"})

    # メンバー追加用の検索
    query = request.GET.get("query")
    if query:
        # 名前、ジョブ、ステータスの一部で検索
        users = User.objects.filter(
            name__icontains=query
        ) | User.objects.filter(
            statuses__category__status_name__icontains=query
        )
    else:
        users = User.objects.exclude(parties__party=party)

    return render(request, "gamification/party_edit.html", {
        "party": party,
        "members": members,
        "users": users.distinct(),  # 検索結果
    })

# テンプレートには「誰が」「何をしゃべった」だけを送ってる
# 裏で、セッションでJson形式で履歴保存
@login_required
def gpt(request):
    messages = []

    if request.method == 'POST':
        if 'reset' in request.POST:  # 会話のリセット
            if 'messages' in request.session:
                del request.session['messages']
            return redirect('gpt')
        
        question = request.POST.get('question')  # ユーザーからの質問を取得
        api_key = request.user.gpt_key  # ログインユーザーのGPTキーを取得

        if 'messages' in request.session:
            messages = request.session['messages']
            messages = [
                HumanMessage(content=msg['content']) if msg['role'] == 'human' else 
                AIMessage(content=msg['content']) if msg['role'] == 'ai' else 
                SystemMessage(content=msg['content'])
                for msg in messages
            ]
        else:
            messages = [
                SystemMessage(content="""あなたは現代を生きる、様々な仕事という名の冒険を行っている冒険者のクエスト(仕事)をサポートをする「何でも相談屋」の主人です。
                                  冒険者の相談ごとに乗り、その依頼を解決できるようにサポートしてください。
                                  また、口調は馴れ馴れしくもどこか憎めないキャラをイメージしてください。
                                  """)
            ]

        messages.append(HumanMessage(content=question))

        try:
            chat = ChatOpenAI(
                openai_api_key=api_key,
                openai_api_base="https://api.openai.iniad.org/api/v1",
                model_name="gpt-4o-mini",
                temperature=0.2
            )
            result = chat(messages)
            messages.append(result)
        except Exception as e:
            messages.append(AIMessage(content="エラーが発生しました: " + str(e)))

        messages_to_save = [
            {'role': 'human', 'content': msg.content} if isinstance(msg, HumanMessage) else 
            {'role': 'ai', 'content': msg.content} if isinstance(msg, AIMessage) else
            {'role': 'system', 'content': msg.content}
            for msg in messages
        ]

        request.session['messages'] = messages_to_save

    context = {
        'messages': [
            {'type': type(msg).__name__, 'content': msg.content} for msg in messages
        ],
        'user': request.user
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

# 以下追加

from django.shortcuts import render
from .models import Party

def party_list_view(request):
    # パーティと、そのメンバーのUserクエリを1発で取得
    parties = Party.objects.prefetch_related('members__user')  # membersを通じてuserを間接的に取得 

    context = {
        'parties': parties,
    }
    return render(request, 'gamification/party_list.html', context)

from django.shortcuts import render
from .models import User  # Userモデルをインポート

def user_list_view(request):
    users = User.objects.all()  # すべてのユーザを取得

    context = {
        'users': users,
    }
    return render(request, 'gamification/user_list.html', context)  # 新しいテンプレートuser_list.htmlにデータを渡す

import random
from django.shortcuts import render
from .models import User

def member_select(request):
    users = User.objects.all()  # すべてのユーザーを取得
    if users.exists():  # ユーザーが存在する場合
        num_users_to_select = 4  # 選ぶユーザーの数
        random_users = random.sample(list(users), min(num_users_to_select, users.count()))  # ランダムにユーザーを選択
    else:
        random_users = []  # ユーザーがいない場合

    context = {
        'random_users': random_users,
    }
    return render(request, 'gamification/member_select.html', context)  # 新しいテンプレートrandom_users.htmlにデータを渡す
def toppage(request):
    return render(request, "gamification/224toppage.html") 


def main_login(request):
    return render(request, "gamification/224login.html")
