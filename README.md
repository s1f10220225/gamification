# gamification
チーム実習

# 開発時
```
cd パス
.\venv\Scripts\activate
code .
```

サーバーの起動(動作確認)
```
python manage.py runserver
```

データベースの更新
```
python manage.py makemigrations
python manage.py migrate
```

スーパーユーザーの作成
```
python manage.py createsuperuser
```

# 初回のみ
```
cd パス
```

仮想環境の構築(Win)
```
python -m venv venv
.\venv\Scripts\activate
```

(仮想環境になってることを確認して)DjangoやOpenAI関連のインストール
```
pip install django
pip install openai langchain langchain-community langchain-core requests
```

# PMだけだから以下は不要
```
django-admin startproject config ./

python manage.py startapp gamification
```