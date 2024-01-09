from django.urls import path
from . import views

urlpatterns = [
    path('', views.Dashboard.as_view(), name='telegram_dashboard'),
    path('mensagens/', views.MensagensView.as_view(), name='telegram_mensagens'),
    path('mensagens/criar/', views.CreateMessageView.as_view(), name='telegram_create_message'),

    path('leads/', views.LeadsView.as_view(), name='telegram_leads'),
    path('leads/criar/', views.CreateLeadView.as_view(), name='telegram_create_lead'),
    path('leads/delete', views.delete_lead, name='telegram_delete_lead'),
]