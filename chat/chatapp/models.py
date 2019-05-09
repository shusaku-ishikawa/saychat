from django import forms
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
import os
from django.db.models import Q
# Create your models here.
import unicodedata
from django.core.files.storage import FileSystemStorage
from django.utils.safestring import mark_safe 

class MyFileSystemStorage(FileSystemStorage):
    """
    Convert unicode characters in name to ASCII characters.
    """
    def get_valid_name(self, name):
        name = unicodedata.normalize('NFC', name)
        return super(MyFileSystemStorage, self).get_valid_name(name)





class MyUserManager(BaseUserManager):
    """ユーザーマネージャー."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """メールアドレスでの登録を必須にする"""
        if not email:
            raise ValueError('The given email must be set')

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """is_staff(管理サイトにログインできるか)と、is_superuer(全ての権限)をFalseに"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """スーパーユーザーは、is_staffとis_superuserをTrueに"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = 'ユーザ'
        verbose_name_plural = 'ユーザ'

    """カスタムユーザーモデル."""
    email = models.EmailField('メールアドレス', max_length=150, null = False, blank=False, unique = True)
    name = models.CharField('名前', max_length=150, null = False, blank=False)
    furigana = models.CharField('フリガナ', max_length = 150, null = False, blank = False)
    birthday = models.DateField(
        verbose_name = _('生年月日'), 
        null = True,
    ) 
    address = models.CharField('住所', max_length = 150, null = True)
    phone = models.CharField('連絡先電話番号', max_length = 50, null = True)
    clinic_name = models.CharField('歯科医院名', max_length = 100, null = True)
    thumbnail = models.ImageField('サムネイル', upload_to = 'profile_thumbnail', null = True)

    is_staff = models.BooleanField(
        '管理者',
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        '有効',
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = MyUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name',]

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def username(self):
        """username属性のゲッター

        他アプリケーションが、username属性にアクセスした場合に備えて定義
        メールアドレスを返す
        """
        return self.email
    @property
    def thumbnail_url(self):
        if self.thumbnail and hasattr(self.thumbnail, 'url'):
            return self.thumbnail.url

class ChatRoom(models.Model):
    def __str__(self):
        return self.title

    title = models.CharField(
        max_length = 50,
    )

    @property
    def group_name(self):
        """
        Returns the Channels Group name that sockets should subscribe to to get sent
        messages as they are generated.
        """
        return "room-%s" % self.pk

    @property
    def get_latest_message(self):
        my_messages = self.messages.all().order_by('-pk')
        if len(my_messages) > 0:
            return my_messages[0]
        return '会話がありません'
    
    def is_member(self, user_id):
        user = User.objects.get(pk = user_id)
        return len(self.members.filter(user = user)) > 0

    @staticmethod
    def get_room_of_us(user_1, user_2):
        for room in ChatRoom.objects.all():
            user_1_mem = ChatRoomMember.objects.filter(user = user_1).filter(room = room)
            user_2_mem = ChatRoomMember.objects.filter(user = user_2).filter(room = room)
            if len(user_1_mem) != 0 and len(user_2_mem) != 0:
                return room
        return None
            
class ChatRoomMember(models.Model):
    def __str__(self):
        return self.room.title + '_' + self.user.name
    room = models.ForeignKey(
        to = ChatRoom,
        on_delete = models.CASCADE,
        related_name = 'members'
    )
    user = models.ForeignKey(
        to = User,
        on_delete = models.CASCADE,
        related_name = 'rooms'
    )
    
    @property
    def opponent(self):
        other_members = ChatRoomMember.objects.filter(room = self.room).filter(~Q(user = self.user))
        if len(other_members) > 0:
            return other_members[0]

class ChatMessage(models.Model):
    def __str__(self):
        return self.message[:5] + '...'

    room = models.ForeignKey(
        to = ChatRoom,
        on_delete = models.CASCADE,
        related_name = 'messages'
    )
    speaker = models.ForeignKey(
        to = User,
        on_delete = models.CASCADE,
        related_name = 'messages'
    )
    message = models.TextField(
    )
    sent_at = models.DateTimeField(
        auto_now_add = True
    )
    @property
    def caption(self):
        if len(self.message) < 10:
            return self.message
        else:
            return self.message[:10] + '...'
    @property
    def message_safe(self): 
        return mark_safe(self.my_textfield)
class Attachment(models.Model):
    def __str__(self):
        return self.file.name
    class Meta:
        verbose_name = "添付ファイル"
        verbose_name_plural = "添付ファイル"
    
    parent_message = models.ForeignKey(
        to = ChatMessage,
        on_delete = models.CASCADE,
        related_name = 'attachments',
        null = True,
        blank = True,
    )
    file = models.FileField(
        verbose_name = 'ファイル',
        upload_to = 'upload',
        null = False,
        blank = False,
    )
    uploaded_at = models.DateTimeField(
        verbose_name = 'アップロード日時',
        auto_now_add = True,
    )
    @property
    def file_name(self):
        return os.path.basename(self.file.name)
    @property
    def file_url(self):
        return self.file.url
