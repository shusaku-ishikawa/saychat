from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
import os
from django.db.models import Q
import unicodedata
from django.core.files.storage import FileSystemStorage
from django.utils.safestring import mark_safe 
from django.template.loader import get_template
from myauth.models import User


class MyFileSystemStorage(FileSystemStorage):
    """
    Convert unicode characters in name to ASCII characters.
    """
    def get_valid_name(self, name):
        name = unicodedata.normalize('NFC', name)
        return super(MyFileSystemStorage, self).get_valid_name(name)


class ChatRoom(models.Model):
    def __str__(self):
        return self.title
    class Meta:
        verbose_name = 'トークルーム'
        verbose_name_plural = 'トークルーム'
    

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
    def messages(self):
        return self.messages.all().order_by('-pk')
    @property
    def latest_message(self):
        my_messages = self.messages.all().order_by('-pk')
        if len(my_messages) > 0:
            return my_messages[0]
        return None
    
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
    class Meta:
        verbose_name = 'トークルームメンバ'
        verbose_name_plural = 'トークルームメンバ'
        
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
    last_logout = models.DateTimeField(
        verbose_name = '最終ログアウト時間',
        null = True,
        default = timezone.now
    )
    is_reading = models.BooleanField(
        verbose_name = '入室中',
        default = False
    )
    @property
    def opponent(self):
        other_members = ChatRoomMember.objects.filter(room = self.room).filter(~Q(user = self.user))
        if len(other_members) > 0:
            return other_members[0]
    @property
    def opponent_is_reading(self):
        return self.opponent.is_reading
    

class ChatMessage(models.Model):
    def __str__(self):
        return self.message[:5] + '...'
    class Meta:
        verbose_name = 'トークルームメッセージ'
        verbose_name_plural = 'トークルームメッセージ'
    
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
    
    @property
    def is_read(self):
        rm = ChatRoomMember.objects.get(room = self.room, user = self.speaker)
        opponent = rm.opponent
        if opponent.is_reading:
            return True
        else:
            if opponent.last_logout > self.sent_at:
                return True
        return False
    @property
    def read(self):
        rm = ChatRoomMember.objects.get(room = self.room, user = self.speaker)
        if rm.is_reading:
            return True
        else:
            if rm.last_logout > self.sent_at:
                return True
        return False

class Thumbup(models.Model):
    
    sender = models.ForeignKey(
        to = User,
        on_delete = models.CASCADE,
        related_name = 'mythumbups'
    )
    room = models.ForeignKey(
        to = ChatRoom,
        on_delete = models.CASCADE,
    )
    target = models.ForeignKey(
        to = ChatMessage,
        on_delete = models.CASCADE,
        related_name = 'mythumbups'
    )

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
    @property
    def uploaded_user(self):
        return self.parent_message.speaker
