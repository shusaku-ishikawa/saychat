from rest_framework import serializers
from myauth.models import User
from django.contrib.auth import password_validation
from django.core.signing import BadSignature, SignatureExpired, dumps, loads

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'thumbnail', 'is_online', 'last_alerted', 'is_staff')
        read_only_fields = ('id', 'email', 'is_online', 'last_alerted', 'is_staff')

class PasswordResetSerializer(serializers.Serializer):
    new_password_1 = serializers.CharField(required = True)
    new_password_2 = serializers.CharField(required = True)
    token = serializers.CharField(required = True)
    def validate_new_password_1(self, value):
        password_validation.validate_password(value)
        return value
    
    def validate_token(self, value):
        """
        Check that the blog post is about Django.
        """
        try:
            loads(value, max_age=60*10)
        except Exception:
            raise serializers.ValidationError('トークンが不正です')
        else:
            return value
    def validate(self, data):
        if data['new_password_1'] != data['new_password_2']:
            raise serializers.ValidationError('パスワードが一致しません')
        return data
    def save(self):
        user_pk = loads(self.validated_data['token'], max_age=60*10)
        user = User.objects.get(id = user_pk)
        user.set_password(self.validated_data['new_password_1'])
        return user
class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password_1 = serializers.CharField()
    new_password_2 = serializers.CharField()

    def validate_new_password_1(self, value):
        password_validation.validate_password(value)
        return value
    def validate(self, data):
        if data['new_password_1'] != data['new_password_2']:
            raise serializers.ValidationError({ 'new_password_1': 'パスワードが一致しません'})
        return data