from django.contrib import admin
from .models import User, Category, Status, Party, PartyBelonged, Quest, Manager # models.pyからモデルを読み込む

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'employee_number', 'name', 'gpt_key', 'is_active', 'is_staff')
    search_fields = ('employee_number', 'name')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_name', 'status_name')
    search_fields = ('category_name', 'status_name')

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'category', 'parameter')
    search_fields = ('user__name', 'category__category_name')
    list_filter = ('category',)

@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('party_id', 'name')
    search_fields = ('name',)

@admin.register(PartyBelonged)
class PartyBelongedAdmin(admin.ModelAdmin):
    list_display = ('id', 'party', 'user', 'role')
    search_fields = ('party__name', 'user__name', 'role')
    list_filter = ('party',)

@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ('quest_id', 'party', 'requester', 'title', 'difficulty', 'status')
    search_fields = ('title', 'requester__name')
    list_filter = ('status', 'difficulty')

@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('id', 'quest', 'assignee')
    search_fields = ('quest__title', 'assignee__name')