from django.shortcuts import render, redirect
from django.http import Http404

# Create your views here.

def top(request):
    return render(request, "gamification/top.html")