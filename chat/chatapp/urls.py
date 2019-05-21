# chat/urls.py
from django.conf.urls import url
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'chatapp'

urlpatterns = [
    path('', views.Login.as_view(), name = "login"),
    path('sign_up/', views.SignUp.as_view(), name='sign_up'),
    path('sign_up/done/<token>', views.SignUpDone.as_view(), name='sign_up_done'),
    path('logout', views.LogoutView.as_view(), name = "logout"),
    path('history', views.history, name = "history"),
    path('upload', views.upload_file, name = "upload"),
    path('user_update/<int:pk>/', views.UserUpdate.as_view(), name='user_update'),
    url(r'^top$', views.Top.as_view(), name='top'),
    path('test/', views.TestView.as_view(), name="hoge")
]