from rest_framework import serializers
from .models import *
from django.core.exceptions import ObjectDoesNotExist
import time
from datetime import datetime, timedelta

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'name', 'email', 'thumbnail_url')

class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ('pk', 'title')

class ChatRoomMemberSerializer(serializers.ModelSerializer):
    #room = ChatRoomSerializer(many = True, read_only = True)
    user = UserSerializer(many = False, read_only = True)
    class Meta:
        model = ChatRoomMember
        fields = ('room', 'user')
    
class AttachmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attachment
        fields = ('file','file_url', 'file_name')

class TimestampField(serializers.Field):
    def to_representation(self, value):
        return int(time.mktime(value.timetuple())) + 60 * 60 * 9

class ChatMessageSerializer(serializers.ModelSerializer):
    speaker = UserSerializer(many = False, read_only = True)
    room = ChatRoomSerializer(many = False, read_only = True)
    sent_at = TimestampField()
    attachments = AttachmentSerializer(many = True, read_only = True)
    class Meta:
        model = ChatMessage
        fields = ('pk', 'speaker', 'room', 'message', 'attachments', 'sent_at')
  