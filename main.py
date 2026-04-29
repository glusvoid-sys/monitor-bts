import requests
from bs4 import BeautifulSoup
import time
import os
import http.server
import socketserver
import threading

# --- CONFIGURAÇÕES DO TELEGRAM ---
TOKEN = "8711199299:AAFWLWO6s5hwbuC9tTkU4KKVOuwV4255cgg"
CHAT_ID = "8121263752"

# Dicionário com as datas do Chile
SHOWS = {
    "Show Dia 14/10": "https://www.ticketmaster.cl/event/bts-world-tour-arirang-live-2026-scl-venta-general-14-de-octubre", 
    "Show Dia 16/10": "https://www.ticketmaster.cl/event/bts-world-tour-arirang-live-2026-scl-venta-general-16-de-octubre",
    "Show Dia 17/10": "https://www.ticketmaster.cl/event/bts-world-tour-arirang-live-2026-scl-venta-general-17-de-octubre"
}

# Guarda o que o bot viu na última vez em cada site
estados_anteriores = {nome: "" for nome in SHOWS}

# --- FUNÇÃO PARA O RENDER NÃO DESLIGAR O BOT ---
def rodar_servidor():
    # Isso faz o Render achar que o bot é um site e mantém ele vivo
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Servidor de monitoramento rodando na porta {port}")
        httpd.serve_forever()

def enviar_telegram(mensagem):
    url_api = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem}
    try:
        requests.post(url_api, data=payload)
    except Exception as e:
        print(f"Erro ao enviar para o Telegram: {e}")

# Inicia o servidor fantasma em uma "thread" separada
threading.Thread(target=rodar_servidor, daemon=True).start()

print("🚀 Bot Multi-Datas Iniciado! Monitorando 14, 16 e 17 de Outubro...")
enviar_telegram("✅ Monitoramento ATIVO para os shows de 14, 16 e 17/10 no Chile!")

while True:
    for nome_show, url in SHOWS.items():
        try:
            # O bot visita um link de cada vez com um cabeçalho para parecer um navegador real
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            resposta = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(resposta.text, 'html.parser')
            
            # Pega o texto principal da página
            estado_atual = soup.get_text()
            
            # Se o site mudou desde a última vez...
            if estados_anteriores[nome_show] != "" and estado_atual != estados_anteriores[nome_show]:
                mensagem = f"🚨 NOVIDADE NO CHILE!\n\n📅 DATA: {nome_show}\n🔗 Link: {url}"
                enviar_telegram(mensagem)
                print(f"Alteração detectada no {nome_show}!")
            
            estados_anteriores[nome_show] = estado_atual
            
        except Exception as e:
            print(f"Erro ao acessar {nome_show}: {e}")
        
        # Espera 10 segundos entre um link e outro
        time.sleep(10)

    # Descansa por 2 minutos antes de checar tudo de novo
    print("Vigilância completa. Aguardando próximo ciclo...")
    time.sleep(120)
