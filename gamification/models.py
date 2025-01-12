from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# カスタムユーザーマネージャーの定義
class CustomUserManager(BaseUserManager):
    def create_user(self, name, gpt_key, password=None):
        if not name:
            raise ValueError('名前は必須です。')
        if not gpt_key:
            raise ValueError('GPTキーは必須かつ、ユニークな値です。')
        user = self.model(name=name, gpt_key=gpt_key)
        user.set_password(password)
        user.save(using=self._db)
        user.employee_number = f"INIAD{user.user_id:06}"  # user_idから社員番号を生成
        user.save(using=self._db)
        print(f"正しい社員番号: INIAD{user.user_id:06}")
        return user

    def create_superuser(self, employee_number, name, gpt_key, password=None):
        user = self.create_user(
            name=name,
            gpt_key=gpt_key,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

# カスタムユーザーモデルの定義
class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)            # ユーザーの識別用ID。AutoFieldだからunique不要
    employee_number = models.CharField(max_length=100, unique=True)  # 社員番号
    name = models.CharField(max_length=100)                 # ユーザーの名前
    gpt_key = models.CharField(max_length=100) # ChatGPTのAPIキー
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'employee_number'    # ログイン時に使うpassword以外のやつ
    REQUIRED_FIELDS = ['name', 'gpt_key'] # スーパーユーザーとか、手動で作成するときに入れるやつ

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
    