# chat/consumers.py
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json
from .models import * 
from .serializer import *
from django.conf import settings
from channels.db import database_sync_to_async



class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        # Are they logged in?
        if self.scope["user"].is_anonymous:
            # Reject the connection
            await self.close()
        else:
            await self.accept()
        self.rooms = set()
            
            

    async def disconnect(self, close_code):
        # Leave room group
        for room_id in list(self.rooms):
            try:
                await self.leave_room(room_id)
            except Exception:
                pass

    # Receive message from WebSocket
    async def receive_json(self, content):
        """
        Called when we get a text frame. Channels will JSON-decode the payload
        for us and pass it as the first argument.
        """
        # Messages will have a "command" key we can switch on
       
        command = content.get("command", None)
     
        if command == "join":
            # Make them join the room
            print('join')
            await self.join_room(content["room"])
        elif command == "leave":
            # Leave the room
            await self.leave_room(content["room"])
        elif command == "send":
            print('commend send')
            await self.send_room(content["room"], content["message"], content['attachment'])


    async def join_room(self, room_id):
        """
        Called by receive_json when someone sent a join command.
        """
        # The logged-in user is in our scope thanks to the authentication ASGI middleware
        print('join_room called')
        
        room = await self._get_room_by_pk(room_id)
        user = self.scope['user']

        if not room.is_member(user.pk):
            await self._create_member_instance(room, self.scope['user'])
            

        # Send a join message if it's turned on
        if True:
            await self.channel_layer.group_send(
                room.group_name,
                {
                    "type": "chat.join",
                    "room_id": room_id,
                    "username": self.scope["user"].username,
                }
            )
        # Store that we're in the room
        self.rooms.add(room_id)
        # Add them to the group so they get room messages
        await self.channel_layer.group_add(
            room.group_name,
            self.channel_name,
        )
        # Instruct their client to finish opening the room
        self.send_json({
            "join": str(room.pk),
            "title": room.title,
        })

    async def leave_room(self, room_id):
        """
        Called by receive_json when someone sent a leave command.
        """
        # The logged-in user is in our scope thanks to the authentication ASGI middleware
        room = await self._get_room_by_pk(room_id)
        user = self.scope['user']

        # Send a leave message if it's turned on
        if settings.NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
            await self.channel_layer.group_send(
                room.group_name,
                {
                    "type": "chat.leave",
                    "room_id": room_id,
                    "username": self.scope["user"].username,
                }
            )
        # Remove that we're in the room
        self.rooms.discard(room_id)

        # Remove them from the group so they no longer get room messages
        await self.channel_layer.group_discard(
            room.group_name,
            self.channel_name,
        )

        # Instruct their client to finish closing the room
        await self.send_json({
            "leave": str(room.id),
        })

    async def send_room(self, room_id, message, attachment_list):
        """
        Called by receive_json when someone sends a message to a room.
        """
        # Check they are in this room
        if room_id not in self.rooms:
            raise Exception
        # Get the room and send to the group about 
        user = self.scope['user']
        room = await self._get_room_by_pk(room_id)
        m = await self._create_new_message(user, room, message)
        
        print('attachment: ' + str(attachment_list))
        for pk in attachment_list:
            a = await self._get_attachment_by_pk(pk)
            await self._set_attachment_to_message(a, m)

        print('send group called')
        await self.channel_layer.group_send(
            room.group_name,
            {
                "type": "chat.message",
                "message_id": m.pk,
            }
        )

    ##### Handlers for messages sent over the channel layer

    # These helper methods are named by the types we send - so chat.join becomes chat_join
    async def chat_join(self, event):
        """
        Called when someone has joined our chat.
        """
        # Send a message down to the client
        print('chat join called')
        await self.send_json(
            {
                "msg_type": settings.MSG_TYPE_ENTER,
                "room": event["room_id"],
                "username": event["username"],
            },
        )

    async def chat_leave(self, event):
        """
        Called when someone has left our chat.
        """
        # Send a message down to the client
        await self.send_json(
            {
                "msg_type": settings.MSG_TYPE_LEAVE,
                "room": event["room_id"],
                "username": event["username"],
            },
        )

    async def chat_message(self, event):
        """
        Called when someone has messaged our chat.
        """
        # Send a message down to the client

        message = await self._get_message_by_pk(event['message_id'])
        serialized = ChatMessageSerializer(message, many = False)
        print('chat message called')
        await self.send_json(
            {
                "msg_type": settings.MSG_TYPE_MESSAGE,
                "message": json.dumps(serialized.data),
            },
        )
    @database_sync_to_async
    def _get_room_by_pk(self, room_id):
        return ChatRoom.objects.get(pk = room_id)

    @database_sync_to_async
    def _create_member_instance(self, room, user):
        new_mem = ChatRoomMember()
        new_mem.room = room
        new_mem.user = user
        new_mem.save()
    @database_sync_to_async
    def _create_new_message(self, user, room, message):
        m = ChatMessage(speaker = user , room = room, message = message)
        m.save()
        return m
    @database_sync_to_async
    def _get_message_by_pk(self, pk):
        return ChatMessage.objects.get(pk = pk)
    @database_sync_to_async
    def _get_attachment_by_pk(self, pk):
        return Attachment.objects.get(pk = pk)
    @database_sync_to_async
    def _set_attachment_to_message(self, attachment, message):
        attachment.parent_message = message
        attachment.save()
