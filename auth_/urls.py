from django.urls import path
from . import views

urlpatterns = [
    path('', views.LoginView.as_view(), name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
]
