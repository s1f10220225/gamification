from django.urls import path
from . import views

urlpatterns = [
    path('', views.top, name='top'),  # 修正
    path('259', views.quest, name='quest'),
    path('quest/<int:quest_id>/', views.quest_detail, name='quest_detail'),  # 修正
    path('quest/add/', views.add_quest, name='add_quest'),  # クエスト追加用のURLパターン
    path('225/gpt', views.gpt, name='gpt'),
]