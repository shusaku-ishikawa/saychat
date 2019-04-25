# chat/consumers.py
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from .models import * 
from .serializer import *
class ChatConsumer(WebsocketConsumer):
    def connect(self):
        
        self.room_pk = self.scope['url_route']['kwargs']['room_pk']
        self.room_group_name = 'chat_%s' % self.room_pk

        user = self.scope['user']
        print(user.name + ' joined ')
        exists = ChatRoom.objects.filter(pk = self.room_pk)
        
        # if the room is not yet created
        if len(exists) == 0:
            room = ChatRoom(pk = self.room_pk)
            room.save()
        else:
            room = exists[0]
        
        members = room.members.all()
        am_i_member = len(members.filter(user = user)) > 0
        
        if not am_i_member:
            new_member = ChatRoomMember(room = room, user = user)
            new_member.save()

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        
        message = text_data_json['message']
        user = self.scope['user']
        room = ChatRoom.objects.get(pk = self.room_pk)
        
        m = ChatMessage(speaker = user , room = room, message = message)
        m.save()

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'message_pk': m.pk
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        #message = event['message']
        message_pk = event['message_pk']

        message = ChatMessage.objects.get(pk = message_pk)
        serializer = ChatMessageSerializer(message, many = False)

        self.send(text_data=json.dumps(serializer.data))