from rest_framework import viewsets
from myauth.models import User
from myauth.serializer import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from myauth.enums import *
from rest_framework import status
import json, math
from django.http import Http404, HttpResponseBadRequest, JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, dumps, loads
from django.views import generic


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = User.objects.get(id = token.user_id)
        user_data = UserSerializer(user, many = False).data
        return Response({'token': token.key, 'user': user_data })

class SignUpView(APIView):
    permission_classes = []
    authentication_classes = []
    serializer_class = UserSerializer
    
    def post(self, request, format=None):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            current_site = get_current_site(request)
            domain = current_site.domain

            bankinfo = BankInfo.get_bank_info()

            context = {
                'protocol': self.request.scheme,
                'domain': domain,
                'token': dumps(user.pk),
                'user': user,
                'bank': bankinfo.bank,
                'branch': bankinfo.branch,
                'meigi': bankinfo.meigi,
                'type': bankinfo.type,
                'number': bankinfo.number
            }
            subject = get_template('mail_template/create/subject.txt').render(context)
            message = get_template('mail_template/create/message.txt').render(context)
            # subject_for_admin =  get_template('mail_template/create_to_admin/subject.txt').render(context)
            # message_for_admin = get_template('mail_template/create_to_admin/message.txt').render(context)

            # for su in User.objects.filter(is_superuser = True):
            #     su.email_user(subject_for_admin, message_for_admin)
            user.email_user(subject, message)
            return Response(status = status.HTTP_200_OK, data = {})
        else:
            print(serializer.errors)
            return Response(status = status.HTTP_400_BAD_REQUEST, data = serializer.errors)
        return None

class PasswordResetView(APIView):
    permission_classes = []
    authentication_classes = []
    serializer_class = None
    
    def get(self, request, format=None):
        email = request.GET.get('email')
        print(email)
        user = get_object_or_404(User, email = email)

        context = {
            'token': dumps(user.pk),
            'user': user
        }
        subject = get_template('mail_template/password_reset/subject.txt').render(context)
        message = get_template('mail_template/password_reset/message.txt').render(context)
        user.email_user(subject, message)
        return Response(status = status.HTTP_200_OK, data = {})  
    def post(self, request, format=None):
        """tokenが正しければ本登録."""
        serializer = PasswordResetSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(status = status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response(status = status.HTTP_400_BAD_REQUEST, data = serializer.errors)

class PasswordChangeView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)         
    serializer_class = PasswordChangeSerializer
    def post(self, request, format = None):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.data.get('old_password')):
                return Response(status=status.HTTP_400_BAD_REQUEST, data = {'old_password': ['現在のパスワードが異なります']})
            # set_password also hashes the password that the user will get
            user.set_password(serializer.data.get('new_password_1'))
            user.save()
            return Response(status = status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response(status = status.HTTP_400_BAD_REQUEST, data = serializer.errors)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # def partial_update(self, request, pk = None):
    #     print(request.data)
    #     return super().partial_update(request, pk)
