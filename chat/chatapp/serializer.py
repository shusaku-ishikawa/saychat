from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from .models import *
from django.core.exceptions import ObjectDoesNotExist

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

    
class ChatMessageSerializer(serializers.ModelSerializer):
    speaker = UserSerializer(many = False, read_only = True)
    room = ChatRoomSerializer(many = False, read_only = True)
    sent_at = serializers.DateTimeField(format="%m/%d %H:%M")
    attachments = AttachmentSerializer(many = True, read_only = True)
    class Meta:
        model = ChatMessage
        fields = ('pk', 'speaker', 'room', 'message', 'attachments', 'sent_at')
  