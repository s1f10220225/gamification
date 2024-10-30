from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('show_image<str:category>/', views.show_image, name='show_image'),
]