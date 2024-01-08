from django.contrib import admin
from . import models

@admin.register(models.Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'criado']
    search_fields = ['titulo', 'texto']
