from django.db import models
from django.contrib.auth.models import User

class Mensagem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    texto = models.TextField()
    criado = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.titulo
    class Meta:
        verbose_name = 'Mensagem'
        verbose_name_plural = 'Mensagens'
        ordering = ['-criado']

class Lead(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    grupo = models.CharField(max_length=100, null=True, blank=True)
    bot_token = models.CharField(max_length=100, null=True, blank=True)
    titulo = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
    class Meta:
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'

class LeadBody(models.Model):
    horario = models.CharField(max_length=100)
    mensagens = models.ManyToManyField(Mensagem)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    criado = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.nome
    class Meta:
        verbose_name = 'Lead Group'
        verbose_name_plural = 'Lead Groups'
        ordering = ['-criado']