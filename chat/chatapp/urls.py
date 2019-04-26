# chat/urls.py
from django.conf.urls import url
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'chatapp'

urlpatterns = [
    path('', views.Login.as_view(), name = "login"),
    path('logout', views.LogoutView.as_view(), name = "logout"),
    path('history', views.history, name = "history"),
    url(r'^top$', views.Top.as_view(), name='top'),
    url(r'^(?P<room_pk>[^/]+)/$', views.Room.as_view(), name='room'),
]