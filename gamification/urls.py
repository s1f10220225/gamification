from django.urls import path
from . import views

from .views import user_profile 

urlpatterns = [
    path('', views.top, name='top'),
    path('259/', views.quest, name='quest'),
    
    path('quest/<int:quest_id>/', views.quest_detail, name='quest_detail'),
    path('pass/', views.password2, name='password'),
    path('quest/accept/<int:quest_id>/', views.accept_quest, name='accept_quest'),
    path('225/gpt/', views.gpt, name='gpt'),
    path('user/<int:user_id>/status/', views.display_status, name='display_status'),
    path('user/<int:user_id>/career_to_status/', views.career_to_status, name='career_to_status'),
    path('party/create/', views.CreatePartyView.as_view(), name='create_party'),
    path('party/<int:party_id>/', views.PartyDetailView.as_view(), name='party_detail'),
    path('party/<int:party_id>/add_member/', views.AddMemberView.as_view(), name='add_member'),
    path('party/<int:party_id>/remove_member/<int:user_id>/', views.RemoveMemberView.as_view(), name='remove_member'),
    path('create_quest/', views.create_quest, name='create_quest'),
    path('summary/', views.summary, name='summary'),
    path('delete_quest/<int:quest_id>/', views.delete_quest, name='delete_quest'),
    
    path('user/profile/', views.user_profile, name='user_profile'),

    # ユーザー認証関係
    path('accounts/signup/', views.SignUp.as_view(), name='signup'),
    path('accounts/signup/complete/', views.signup_complete, name='signup_complete'),
    path('accounts/login/', views.LoginView.as_view(), name='login'),
]