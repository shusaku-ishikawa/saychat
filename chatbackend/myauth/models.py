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
from django.template.loader import get_template


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
    thumbnail = models.ImageField('サムネイル', upload_to = 'profile_thumbnail', null = True)
    is_online = models.BooleanField(
        verbose_name = 'オンライン',
        default = False
    )
    
    DOES_NOT_NOTIFY = '0'
    NOTIFY_EVERYTIME = '1'
    NOTIFY_ONCE_HALF_HOUR = '2'
    NOTIFY_ONCE_HOUR = '3'
    
    
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

    def notify_new_message(self):
        
        context = {
            'user': self,
        }

        subject_template = get_template('chatapp/mail_template/has_new_message/subject.txt')
        subject = subject_template.render(context)

        message_template = get_template('chatapp/mail_template/has_new_message/message.txt')
        message = message_template.render(context)

        self.email_user(subject, message, fail_silently = True)
        self.last_alerted = timezone.now()
        self.save()

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

