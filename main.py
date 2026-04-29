import requests
from bs4 import BeautifulSoup
import time

# --- CONFIGURAÇÕES DO TELEGRAM ---
TOKEN = "8711199299:AAFWLWO6s5hwbuC9tTkU4KKVOuwV4255cgg"
CHAT_ID = "8121263752" # Coloque o ID que o @userinfobot te deu

# Dicionário com as datas do Chile
SHOWS = {
    "Show Dia 14/10": "https://www.ticketmaster.cl/event/bts-world-tour-arirang-live-2026-scl-venta-general-14-de-octubre", 
    "Show Dia 16/10": "https://www.ticketmaster.cl/event/bts-world-tour-arirang-live-2026-scl-venta-general-16-de-octubre",
    "Show Dia 17/10": "https://www.ticketmaster.cl/event/bts-world-tour-arirang-live-2026-scl-venta-general-17-de-octubre"
    }

# Guarda o que o bot viu na última vez em cada site
estados_anteriores = {nome: "" for nome in SHOWS}

def enviar_telegram(mensagem):
    url_api = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem}
    try:
        requests.post(url_api, data=payload)
    except Exception as e:
        print(f"Erro ao enviar para o Telegram: {e}")

print("🚀 Bot Multi-Datas Iniciado! Monitorando 14, 16 e 17 de Outubro...")
enviar_telegram("✅ Monitoramento ATIVO para os shows de 14, 16 e 17/10 no Chile!")

while True:
    for nome_show, url in SHOWS.items():
        try:
            # O bot visita um link de cada vez
            resposta = requests.get(url, timeout=15)
            soup = BeautifulSoup(resposta.text, 'html.parser')
            
            # Pega o texto principal da página de ingressos
            estado_atual = soup.text 
            
            # Se o site mudou desde a última vez que o bot olhou...
            if estados_anteriores[nome_show] != "" and estado_atual != estados_anteriores[nome_show]:
                mensagem = f"🚨 NOVIDADE NO CHILE!\n\n📅 DATA: {nome_show}\n🔗 Link: {url}"
                enviar_telegram(mensagem)
                print(f"Alteração detectada no {nome_show}!")
            
            estados_anteriores[nome_show] = estado_atual
            
        except Exception as e:
            print(f"Erro ao acessar {nome_show}: {e}")
        
        # Espera 10 segundos antes de ir para o próximo link (segurança)
        time.sleep(10)

    # Após checar os 3 dias, ele descansa por 2 minutos
    print("Vigilância completa. Aguardando próximo ciclo...")
    time.sleep(120)
