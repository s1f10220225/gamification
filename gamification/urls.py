from django.urls import path
from . import views

urlpatterns = [
    path('', views.top, name='top'),
    path('259', views.quest, name='quest'),
    path('quest/<int:quest_id>/', views.quest_detail, name='quest_detail'),
    path('quest/add/', views.add_quest, name='add_quest'),
    path('pass/', views.password2, name='password'),  # パスワード入力ページのURL
    path('quest/accept/<int:quest_id>/', views.accept_quest, name='accept_quest'),  # 受けるURLを追加
    path('quest/delete/<int:quest_id>/', views.delete_quest, name='delete_quest'),
    path('generate-summary/', views.generate_summary, name='generate_summary'),
]