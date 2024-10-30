from django.urls import path
from . import views

urlpatterns = [
    path('', views.top, name='top'),
    path('259', views.quest, name='quest'),
    path('quest/<int:quest_id>/', views.quest_detail, name='quest_detail'),  # 修正
    path('quest/add/', views.add_quest, name='add_quest'),  # クエスト追加用のURLパターン
    path('user/<int:user_id>/status/', views.display_status, name='display_status'),  # ステータス表示用のURL
    path('pass/', views.password2, name='password'),  # パスワード入力ページのURL
    path('quest/accept/<int:quest_id>/', views.accept_quest, name='accept_quest'),  # 受けるURLを追加

    path('225/gpt', views.gpt, name='gpt'), # GPTと会話できるプロトタイプページ

    path('quest/delete/<int:quest_id>/', views.delete_quest, name='delete_quest'),
    path('generate-summary/', views.generate_summary, name='generate_summary'),
    path('generate-difficult/', views.generate_difficult, name='generate_difficult'),

]