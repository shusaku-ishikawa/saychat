from django.contrib import admin
from .models import *
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.utils import quote
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _


# Register your models here.
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('title',)

class ChatRoomMemberAdmin(admin.ModelAdmin):
    list_display = ('room', 'user')

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'speaker', 'message')

admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(ChatRoomMember, ChatRoomMemberAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)

