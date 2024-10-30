from django.db import models

# Create your models here.

# ユーザーを管理するテーブル
class User(models.Model):
    user_id = models.AutoField(primary_key=True)  # ユーザーの識別用ID
    name = models.CharField(max_length=100)  # ユーザーの名前
    gpt_key = models.IntegerField(default=0) # ChatGPTのAPIキー

    def __str__(self):
        return f"{self.name} (ID: {self.user_id})"
    
# スキルカテゴリを管理するテーブル
class Category(models.Model):
    category_name = models.CharField(max_length=100)  # カテゴリ名
    status_name = models.CharField(max_length=100)  # スキル名

    def __str__(self):
        return f"Category: {self.category_name}, Skill: {self.status_name}"

# ユーザーの持つスキルを管理するテーブル
class Status(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='statuses')  # ユーザーの識別用ID
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='statuses', default=1)  # スキルカテゴリの識別用ID
    parameter = models.IntegerField()  # ステータスのパラメータ

    def __str__(self):
        return f"{self.category.status_name} (Parameter: {self.parameter}, User: {self.user.user_id})"


# パーティーを管理するテーブル
class Party(models.Model):
    party_id = models.AutoField(primary_key=True)  # パーティーの識別用ID
    name = models.CharField(max_length=100)  # パーティーの名前

    def __str__(self):
        return f"{self.name} (ID: {self.party_id})"
    

# ユーザーがどのパーティーに所属しているかを管理するテーブル
class PartyBelonged(models.Model):
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='members')  # パーティーの識別用ID
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parties')  # ユーザーの識別用ID
    role = models.CharField(max_length=100)  # 役職名

    def __str__(self):
        return f"Party: {self.party.party_id}, User: {self.user.user_id}, Role: {self.role}"

# クエストの内容やその状態を管理するテーブル
class Quest(models.Model):
    quest_id = models.AutoField(primary_key=True)  # クエストの識別用ID
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='quests')  # パーティーの識別用ID
    requester = models.ForeignKey(User, related_name='requested_quests', on_delete=models.CASCADE)  # 依頼者の識別用ID
    title = models.CharField(max_length=100)  # クエストの見出し、タイトル
    detail = models.TextField()  # クエストの内容
    difficulty = models.CharField(max_length=10)  # クエストの難易度
    time = models.CharField(max_length=100)  # 予測時間
    status = models.CharField(max_length=100, default='未受注')  # クエストの状態。初期値は未受注

    def __str__(self):
        return f"{self.title} (ID: {self.quest_id})"
    

# クエストを誰が担当しているかを管理するテーブル
class Manager(models.Model):
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name='managers')  # クエストの識別用ID
    assignee = models.ForeignKey(User, related_name='assigned_quests', on_delete=models.CASCADE, null=True, blank=True)  # 受注者の識別用ID。初期値はNull

    def __str__(self):
        return f"Quest: {self.quest.quest_id}, Assignee: {self.assignee.user_id if self.assignee else 'None'}"
    