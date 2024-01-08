from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render,redirect
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from . import models
from django.contrib import messages
from django.http import JsonResponse

class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = 'telegram/dashboard.html'
    title = 'Telegram Dashboard'
    login_url = 'login_view'
    login_redirect_url = 'telegram_dashboard'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['page_name'] = 'telegram_dashboard'
        return context
    
class MensagensView(LoginRequiredMixin, ListView):
    template_name = 'telegram/listar/mensagens.html'
    title = 'Mensagens'
    login_url = 'login_view'
    login_redirect_url = 'telegram_mensagens'
    model = models.Mensagem
    ordering = ['-criado']
    context_object_name = 'mensagens'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['page_name'] = 'telegram_mensagens'
        return context
    
    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(user=self.request.user)
    
class CreateMessageView(LoginRequiredMixin, TemplateView):
    template_name = 'telegram/criar/mensagens.html'
    title = 'Criar Mensagem'
    login_url = 'login_view'
    login_redirect_url = 'telegram_create_message'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['page_name'] = 'telegram_mensagens'
        return context
    
    def post(self, request, *args, **kwargs):
        titulo = request.POST.get('titulo')
        texto = request.POST.get('texto')
        models.Mensagem.objects.create(
            user=request.user,
            titulo=titulo,
            texto=texto
        )
        messages.success(request, 'Mensagem criada com sucesso!')
        return redirect('telegram_mensagens')
    
class LeadsView(LoginRequiredMixin, ListView):
    template_name = 'telegram/listar/leads.html'
    title = 'Leads'
    login_url = 'login_view'
    login_redirect_url = 'telegram_leads'
    model = models.Lead
    context_object_name = 'leads'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['page_name'] = 'telegram_leads'

        leads = super().get_queryset().filter(user=self.request.user)
        for lead in leads:
            leadbodys = models.LeadBody.objects.filter(lead=lead).order_by('horario')
            for leadbody in leadbodys:
                leadbody.mens = leadbody.mensagens.all().order_by('titulo')
                print(leadbody.mens)
            lead.leadbodys = leadbodys
        context['leads'] = leads

        return context
    
    
class CreateLeadView(LoginRequiredMixin, TemplateView):
    template_name = 'telegram/criar/leads.html'
    title = 'Criar Lead'
    login_url = 'login_view'
    login_redirect_url = 'telegram_create_lead'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['page_name'] = 'telegram_leads'
        messages = models.Mensagem.objects.filter(user=self.request.user)
        context['mensagens'] = messages
        return context
    
    def post(self, request, *args, **kwargs):
        horarios = request.POST.get('horarios')
        #convertendo horarios de string para dicionario
        horarios = eval(horarios)
        print(horarios)
        
        #verificando se o usuário já possui um Lead
        lead = models.Lead.objects.filter(user=request.user)

        #TODO: DESCOMENTAR ESSAS LINHAS
        # if lead.exists():
        #     lead = lead.first()
        #     messages.add_message(request, messages.ERROR, 'Você já Atingiu o Limite de Leads!')
        #     return JsonResponse({'status': 'error'})
        
        #criando o lead
        lead = models.Lead.objects.create(
            user=request.user,
            titulo=horarios['titulo']
        )
        #tirando o titulo do dicionario
        del horarios['titulo']
        #criando os leadbodys
        for horario, mensagens in horarios.items():
            print(horario)
            leadbody = models.LeadBody.objects.create(
                horario=horario,
                lead=lead
            )
            for mensagem in mensagens:
                print(mensagem)
                leadbody.mensagens.add(mensagem)

        messages.add_message(request, messages.SUCCESS, 'Lead criado com sucesso!')
        return JsonResponse({'status': 'success'})