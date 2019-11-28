from rest_framework import serializers
from .models import *
from django.core.exceptions import ObjectDoesNotExist
import time
from datetime import datetime, timedelta
from myauth.serializer import UserSerializer
from drf_extra_fields.fields import Base64ImageField

class AttachmentSerializer(serializers.ModelSerializer):
    uploaded_user = UserSerializer(many = False, read_only = True)
    class Meta:
        model = Attachment
        fields = ('id', 'file','file_url', 'file_name', 'uploaded_user', 'uploaded_at')

class TimestampField(serializers.Field):
    def to_representation(self, value):
        return int(time.mktime(value.timetuple())) + 60 * 60 * 9

class ThumbupSerializer(serializers.ModelSerializer):
    sender = UserSerializer(many = False, read_only = True)
    class Meta:
        model = Thumbup
        fields = ('id', 'sender')
class ChatMessageSerializer(serializers.ModelSerializer):
    speaker = UserSerializer(many = False, read_only = True)
    sent_at = TimestampField()
    mythumbups = ThumbupSerializer(many = True, read_only = True)
    attachments = AttachmentSerializer(many = True, read_only = True)
    class Meta:
        model = ChatMessage
        fields = ('pk', 'speaker', 'mythumbups', 'message', 'attachments', 'sent_at', 'is_read', 'read')
  
class ChatRoomMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(many = False, read_only = True)
    class Meta:
        model = ChatRoomMember
        fields = ('user', 'opponent_is_reading')

class ChatRoomSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many = True, read_only = True)
    members = ChatRoomMemberSerializer(many = True, read_only = True)
    class Meta:
        model = ChatRoom
        fields = ('id', 'title', 'messages', 'members')

