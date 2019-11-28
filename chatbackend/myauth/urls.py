# chat/urls.py
from django.conf.urls import url
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from rest_framework import routers
app_name = 'myauth'

urlpatterns = [
    path('gettoken/', views.CustomObtainAuthToken.as_view(), name = "gettoken"),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('passwordreset/', views.PasswordResetView.as_view(), name = "passwordreset"),
    path('passwordchange/', views.PasswordChangeView, name = "passwordchange"),
]
router = routers.SimpleRouter()
router.register('users', views.UserViewSet)
urlpatterns += router.urls


