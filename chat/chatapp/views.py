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
from django.urls import reverse, reverse_lazy
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import get_template
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import ModelFormMixin
from .serializer import *

class Top(LoginRequiredMixin, generic.TemplateView):
    template_name = 'chatapp/top.html'
    def get_context_data(self, **kwargs):
        context = super(Top, self).get_context_data(**kwargs)

        if self.request.user.is_staff:
            users = User.objects.filter(is_active = True).filter(is_staff = False)
        else:
            users = User.objects.filter(is_active = True).filter(is_staff = True)
        users_not_spoken_with = []
        for user in users:
            if user != self.request.user:
                if ChatRoom.get_room_of_us(user, self.request.user) == None:
                    users_not_spoken_with.append(user)
                    print('our room not found ' + str(user) + ': ' + str(self.request.user))
                else:
                    print('our room found' + str(user) + ': ' + str(self.request.user))
        
        print(users_not_spoken_with)
        my_rooms = self.request.user.rooms.all()
        context['users'] = users_not_spoken_with
        context['my_rooms'] = my_rooms
       
        return context

def history(request):
    room_pk = request.GET.get('room_pk')
    offset = int(request.GET.get('offset'))
    limit = int(request.GET.get('limit'))

    room = ChatRoom.objects.get(pk = room_pk)

    all_messages = ChatMessage.objects.filter(room = room).order_by('-sent_at')[offset:offset + limit]

    serializered = ChatMessageSerializer(all_messages, many = True).data
    return JsonResponse(serializered, status = 200, safe = False)



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

        subject_template = get_template('chatapp/mail_template/sign_up/subject.txt')
        subject = subject_template.render(context)

        message_template = get_template('chatapp/mail_template/sign_up/message.txt')
        message = message_template.render(context)
        try:
            user.email_user(subject, message)
            messages.success(self.request, '本登録用リンクを送付しました')
        except:
            messages.error(self.request, 'メール送信中にエラーが発生しました')
        
        return  HttpResponseRedirect(reverse('chatapp:sign_up'))

class TestView(generic.TemplateView):
    template_name = 'chatapp/sign_up_done.html'
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
                    # トークルームも作成する
                    if user.is_staff:
                        normal_users = User.objects.filter(is_active = True).filter(is_staff = False)
                        for normal_user in normal_users:
                            new_room = ChatRoom(title = normal_user.name + '×' + user.name)
                            new_room.save()

                            me = ChatRoomMember(room = new_room, user = user)
                            you = ChatRoomMember(room = new_room, user = normal_user)
                            me.save()
                            you.save()
                    else:
                        staffs = User.objects.filter(is_active = True).filter(is_staff = True)
                        for staff in staffs:
                            new_room = ChatRoom(title = user.name + '×' + staff.name)
                            new_room.save()

                            me = ChatRoomMember(room = new_room, user = user)
                            you = ChatRoomMember(room = new_room, user = staff)
                            me.save()
                            you.save()

                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()

class UserUpdate(SuccessMessageMixin, LoginRequiredMixin, generic.UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'chatapp/user_update.html'
    success_message = '登録情報を更新しました'
    def get_success_url(self):
        return resolve_url('chatapp:user_update', pk=self.kwargs['pk'])

class PasswordChange(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    """パスワード変更ビュー"""
    form_class = MyPasswordChangeForm
    success_message = 'パスワードを更新しました'
    success_url = reverse_lazy('chatapp:password_change')
    template_name = 'chatapp/password_change.html'


class PasswordReset(SuccessMessageMixin, PasswordResetView):
    """パスワード変更用URLの送付ページ"""
    subject_template_name = 'chatapp/mail_template/password_reset/subject.txt'
    email_template_name = 'chatapp/mail_template/password_reset/message.txt'
    template_name = 'chatapp/password_reset.html'
    form_class = MyPasswordResetForm
    success_message = "再設定用リンクを送付しました"
    success_url = reverse_lazy('chatapp:password_reset')
    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except:
            messages.error(self.request, 'メール送信中にエラーが発生しました')
            return HttpResponseRedirect(reverse('chatapp:password_reset'))



class PasswordResetConfirm(PasswordResetConfirmView):
    """新パスワード入力ページ"""
    form_class = MySetPasswordForm
    success_url = reverse_lazy('chatapp:password_reset_complete')
    template_name = 'chatapp/password_reset_confirm.html'


class PasswordResetComplete(PasswordResetCompleteView):
    """新パスワード設定しましたページ"""
    template_name = 'chatapp/password_reset_complete.html'

