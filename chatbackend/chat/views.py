from django.shortcuts import render, get_object_or_404
from chat.models import *
from chat.serializer import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import viewsets
from rest_framework.views import APIView
# Create your views here.
from rest_framework.response import Response
from rest_framework import status

class ChatRoomViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    def list(self, request, **kwargs):
        rm_list = request.user.rooms.all()
        rooms = [rm.room for rm in rm_list]
        data = ChatRoomSerializer(rooms, many = True).data
        return Response(status=status.HTTP_200_OK, data = data)

class ChatRoomMemberViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = ChatRoomMember.objects.all()
    serializer_class = ChatRoomSerializer
    def list(self, request, **kwargs):
        rm_list = request.user.rooms.all()
        members = [rm.opponent for rm in rm_list]
        data = ChatRoomMemberSerializer(members, many = True).data
        return Response(status=status.HTTP_200_OK, data = data)

class ChatMessageViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = ChatMessage.objects.all()
    serializer_class = ChatRoomSerializer
    def list(self, request, **kwargs):
        if not 'room' in request.GET:
            return Response(status = status.HTTP_400_BAD_REQUEST)
        room_id = request.GET.get('room')
        room = get_object_or_404(ChatRoom, id = room_id)
        messages = ChatMessage.objects.filter(room = room)

        data = ChatMessageSerializer(messages, many = True).data
        return Response(status=status.HTTP_200_OK, data = data)

class ChatMessageAttachmentView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    def get(self, request):
        if 'room' not in request.GET:
            return Response(status = status.HTTP_400_BAD_REQUEST)
        room = get_object_or_404(ChatRoom, id = request.GET.get('room'))
        attachments = Attachment.objects.filter(parent_message__room = room)
        print(attachments)
        data = AttachmentSerializer(attachments, many = True).data
        return Response(status = status.HTTP_200_OK, data = data)
        
    def post(self, request):
        files = request.FILES
        print(files)
        obj_list = []
        for file in files:
            obj = Attachment()
            obj.file.save(file.name, file)
            obj.save()
            obj_list.append(obj)

        data = AttachmentSerializer(obj_list, many = True).data
        return Response(status = status.HTTP_200_OK, data = data)

class ThumbupView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    def get(self, request):
        if 'room' not in request.GET:
            return Response(status = status.HTTP_400_BAD_REQUEST)
        room = get_object_or_404(ChatRoom, id = request.GET.get('room'))
        attachments = Attachment.objects.filter(parent_message__room = room)
        print(attachments)
        data = AttachmentSerializer(attachments, many = True).data
        return Response(status = status.HTTP_200_OK, data = data)
        
    def post(self, request):
        print(request.data)
        action = request.data.get('action')
        target_message_id = request.data.get('target')
        if not action or not target_message_id:
            print('invalid parameter')
            return Response(status = status.HTTP_400_BAD_REQUEST)
        if action == 'add':
            target_message = ChatMessage.objects.get(id = target_message_id)
            room = target_message.room
            sender = request.user
            try:
                Thumbup.objects.get(target = target_message, sender = sender)
                instance.save()
                return Response(status = status.HTTP_200_OK)
            except Thumbup.DoesNotExist:
                instance = Thumbup(sender = sender, target = target_message, room = room)
            else:
                return Response(status = status.HTTP_200_OK)
        elif action == 'delete':
            pass