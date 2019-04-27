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

def history(request):
    room_pk = request.GET.get('room_pk')
    offset = int(request.GET.get('offset'))
    limit = int(request.GET.get('limit'))

    room = ChatRoom.objects.get(pk = room_pk)

    all_messages = ChatMessage.objects.filter(room = room).order_by('-sent_at')[offset:offset + limit]

    serializer = ChatMessageSerializer(all_messages, many = True)
    return JsonResponse(serializer.data, status = 200, safe = False)

def upload_file(request):
    method = request.method

    if method == 'POST':
        if request.POST.get('method') == 'DELETE':
            pk = request.POST.get('pk')
            Attachment.objects.filter(pk=pk).delete()
            return JsonResponse({'success': True})
        else:
            a = Attachment()
            a.file = request.FILES['attachment']
            a.save()
            return JsonResponse({'success': True, 'pk': a.pk, 'url': a.file.url})

class Login(LoginView): # 追加
    """ログインページ"""
    form_class = LoginForm
    template_name = 'chatapp/login.html'

class SignUp(generic.CreateView):
    """ユーザー仮登録"""
    template_name = 'chatapp/sign_up.html'
    form_class = SignUpForm
   
    def form_valid(self, form):
        """仮登録と本登録用メールの発行."""
        # 仮登録と本登録の切り替えは、is_active属性を使うと簡単です。
        # 退会処理も、is_activeをFalseにするだけにしておくと捗ります。
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': self.request.scheme,
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        subject_template = get_template('amazon/mail_template/sign_up/subject.txt')
        subject = subject_template.render(context)

        message_template = get_template('amazon/mail_template/sign_up/message.txt')
        message = message_template.render(context)

        user.email_user(subject, message)
        messages.success(self.request, '本登録用リンクを送付しました')
        return  HttpResponseRedirect(reverse('chatapp:sign_up'))

class SignUpDone(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'chatapp/sign_up_done.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # 問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    # カートも作成する
                    his_cart = ShoppingCart()
                    his_cart.user = user
                    his_cart.save()

                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()