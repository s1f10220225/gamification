from django.urls import path
from . import views

from .views import user_profile 
from .views import party_list_view

urlpatterns = [
    path('top', views.top, name='top'),
    path('259/', views.quest, name='quest'),
    
    path('quest/<int:quest_id>/', views.quest_detail, name='quest_detail'),
    path('pass/', views.password2, name='password'),
    path('quest/accept/<int:quest_id>/', views.accept_quest, name='accept_quest'),
    path('225/gpt/', views.gpt, name='gpt'),
    path('user/status/', views.display_status, name='display_status'),
    path('user/career_to_status/', views.career_to_status, name='career_to_status'),
    # path('party/create/', views.CreatePartyView.as_view(), name='create_party'),
    # path('party/<int:party_id>/', views.PartyDetailView.as_view(), name='party_detail'),
    # path('party/<int:party_id>/add_member/', views.AddMemberView.as_view(), name='add_member'),
    # path('party/<int:party_id>/remove_member/<int:user_id>/', views.RemoveMemberView.as_view(), name='remove_member'),
    path('create_quest/', views.create_quest, name='create_quest'),
    path('summary/', views.summary, name='summary'),
    path('delete_quest/<int:quest_id>/', views.delete_quest, name='delete_quest'),
    
    path('user/profile/', views.user_profile, name='user_profile'),
    path('parties/', views.party_list_view, name='party-list'),
    path('users/', views.user_list_view, name='user-list'),  # 新しいURLパターンを追加
    path('member_select/', views.member_select, name='member_select'), 

    # パーティー関連
    path("party/dashboard/", views.party_dashboard, name="party_dashboard"),
    path("party/create/", views.create_party, name="create_party"),
    path("party/<int:party_id>/", views.party_detail, name="party_detail"),
    path("party/<int:party_id>/optimize/", views.optimize_party, name="optimize_party"),
    path("party/<int:party_id>/edit/", views.edit_party, name="edit_party"),

    # ユーザー認証関係
    path('accounts/signup/', views.SignUp.as_view(), name='signup'),
    path('accounts/signup/complete/', views.signup_complete, name='signup_complete'),
    path('accounts/login/', views.LoginView.as_view(), name='login'),

    path('224toppage',views.toppage,name='toppage'),
    path('',views.main_login,name='main_login'),

    
]