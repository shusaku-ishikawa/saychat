from django.shortcuts import render
from django.utils.safestring import mark_safe
import json

from django.shortcuts import render
from django.views import generic
from .models import * 
from django.contrib.auth.views import *
from .forms import *
from django.contrib.auth.mixins import LoginRequiredMixin

from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.core.signing import BadSignature, SignatureExpired, dumps, loads
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import get_template
from django.contrib import messages
from django.views.generic.edit import ModelFormMixin
from .serializer import *

class Top(LoginRequiredMixin, generic.TemplateView):
    template_name = 'chatapp/top.html'
    def get_context_data(self, **kwargs):
        context = super(Top, self).get_context_data(**kwargs)
        users = User.objects.all()
        all_rooms = ChatRoom.objects.all()
        my_rooms = self.request.user.rooms.all()
        context['users'] = users
        context['my_rooms'] = my_rooms
        context['all_rooms'] = all_rooms
        return context


class Room(LoginRequiredMixin, generic.TemplateView):
    template_name = 'chatapp/room.html'
    def get_context_data(self, **kwargs):
        context = super(Room, self).get_context_data(**kwargs)
        room_pk = kwargs['room_pk']
        room = ChatRoom.objects.get(pk = room_pk)

        
        all_messages = ChatMessage.objects.all()
        
        context['room'] = room
        context['messages'] = all_messages
        return context

def room(request, room_pk):
    return render(request, 'chatapp/room.html', {
        'room_pk': room_pk
    })

def history(request, room_pk):
    all_messages = ChatMessage.objects.all()
    serializer = ChatMessageSerializer(all_messages, many = True)
    return JsonResponse(serializer.data, status = 200, safe = False)

class Login(LoginView): # 追加
    """ログインページ"""
    form_class = LoginForm
    template_name = 'chatapp/login.html'

