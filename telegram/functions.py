import schedule
import time
from datetime import datetime, timedelta
import threading
import random
from .models import *
import requests

def tarefa_a_ser_executada(horario):
    leads = LeadBody.objects.filter(horario=horario)
    if leads.exists():
        for lead in leads:
            token = lead.lead.bot_token
            chat_id = lead.lead.chat

            mensagem = lead.mensagens

            url_base = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={mensagem}'
            requests.get(url_base)


    print("leads encontrados=",leads)

def agendar_tarefas():
    # Adicione as tarefas que você deseja executar em momentos específicos aqui
    for i in range(0, 24):
        if i < 10:
            i = f"0{i}"
        for j in range(0, 60, 5):
            if j < 10:
                j = f"0{j}"
            #adicionando função no schedule e passando o horário como parâmetro
            schedule.every().day.at(f"{i}:{j}").do(tarefa_a_ser_executada, horario=f"{i}:{j}")

    while True:
        schedule.run_pending()
        time.sleep(1)

def chamar_agendador():
    t = threading.Thread(target=agendar_tarefas)
    t.start()

if __name__ == "__main__":
    agendar_tarefas()