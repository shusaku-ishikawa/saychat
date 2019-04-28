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
  

# class HistorySerializer(serializers.ModelSerializer):
#     unixtimestamp = serializers.IntegerField(source = 'cooked_at')
#     requestId = serializers.SlugRelatedField(source = 'corresponding_query', queryset=RecipeQuery.objects.all(), slug_field='pk')
#     channels = HistoryByChannelSerializer(many = True, write_only = True)
#     powerConsumed = serializers.FloatField(source = 'power_consumed')
#     otherInfo = serializers.CharField(source = 'other_info', allow_blank = True)
#     class Meta:
#         model = History
#         fields = ['unixtimestamp', 'requestId','channels', 'powerConsumed', 'otherInfo']
    
#     def create(self, validated_data):
#         channels = validated_data.pop('channels')
#         history = History.objects.create(**validated_data)

#         for ch in channels:
#             channel = HistoryByChannel(**ch)
#             channel.history = history
#             channel.save()
#         return history
