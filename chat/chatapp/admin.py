from django.contrib import admin
from .models import *
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.utils import quote
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _

class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)


class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('name','furigana', 'birthday', 'thumbnail', 'address', 'email',  'phone', 'password')}),
        (_('Personal info'), {'fields': ('clinic_name',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name','furigana',  'birthday', 'thumbnail', 'clinic_name', 'address','phone', 'email', 'password1', 'password2'),
        }),
    )
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = ('email', 'name', 'thumbnail', 'address', 'furigana', 'phone', 'clinic_name', 'is_staff', 'is_active', 'is_superuser')

    ordering = ('name',)
# Register your models here.
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('title',)

class ChatRoomMemberAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'last_logout', 'is_online')

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'speaker', 'message')

class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('file', 'parent_message')

admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(ChatRoomMember, ChatRoomMemberAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(User, MyUserAdmin)

