from django.urls import path
from . import views

urlpatterns = [
    path('', views.top, name='top'),
    path('259/', views.quest, name='quest'),  # パスの最後にスラッシュ追加
    path('quest/<int:quest_id>/', views.quest_detail, name='quest_detail'),  # 修正

    

    path('user/<int:user_id>/status/', views.display_status, name='display_status'),  # ステータス表示用のURL
    path('pass/', views.password2, name='password'),  # パスワード入力ページのURL
    path('quest/accept/<int:quest_id>/', views.accept_quest, name='accept_quest'),  # 受けるURLを追加
    path('225/gpt/', views.gpt, name='gpt'),  # GPTと会話できるプロトタイプページ
    path('user/<int:user_id>/career_to_status/', views.career_to_status, name='career_to_status'),  # キャリアのステータス化
    path('party/create/', views.CreatePartyView.as_view(), name='create_party'),  # パーティー作成
    path('party/<int:party_id>/', views.PartyDetailView.as_view(), name='party_detail'),  # パーティーの詳細(メンバー一覧)
    path('party/<int:party_id>/add_member/', views.AddMemberView.as_view(), name='add_member'),  # メンバーの追加
    path('party/<int:party_id>/remove_member/<int:user_id>/', views.RemoveMemberView.as_view(), name='remove_member'),  # メンバーの削除


    path('sample/2/', views.combined_view, name='sample_return2'), 
]