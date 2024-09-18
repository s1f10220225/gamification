from django.contrib import admin
from .models import User,Status # models.pyからUserとStatusを読み込む

# Register your models here.
admin.site.register(User) # Userのデータをadminサイトから追加できるように
admin.site.register(Status) # Statusのデータをadminサイトから追加できるように