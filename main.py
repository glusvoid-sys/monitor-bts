import telebot
import requests
from bs4 import BeautifulSoup
import time
import os
import threading
import http.server
import socketserver

# --- CONFIGURAÇÕES ---
TOKEN = "8711199299:AAFWLWO6s5hwbuC9tTkU4KKVOuwV4255cgg"
CHAT_ID = "8121263752"
bot = telebot.TeleBot(TOKEN)

SHOWS = {
    "14/10": "https://www.ticketmaster.cl/event/bts-world-tour-arirang-live-2026-scl-venta-general-14-de-octubre",
    "16/10": "https://www.ticketmaster.cl/event/bts-world-tour-arirang-live-2026-scl-venta-general-16-de-octubre",
    "17/10": "https://www.ticketmaster.cl/event/bts-world-tour-arirang-live-2026-scl-venta-general-17-de-octubre"
}

historico_texto = {data: "" for data in SHOWS}

# --- FUNÇÃO PARA ENGANAR O RENDER (PORTA) ---
def rodar_servidor_fantasma():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

def checar_sites():
    while True:
        for data, url in SHOWS.items():
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                res = requests.get(url, headers=headers, timeout=15)
                soup = BeautifulSoup(res.text, 'html.parser')
                texto_atual = soup.get_text()

                if historico_texto[data] != "" and texto_atual != historico_texto[data]:
                    msg = f"🚨 **MUDANÇA DETECTADA!**\n📅 Show Dia: {data}\n🔗 {url}"
                    bot.send_message(CHAT_ID, msg)
                
                historico_texto[data] = texto_atual
            except Exception as e:
                print(f"Erro no monitor: {e}")
            time.sleep(10)
        time.sleep(120)

# --- COMANDOS ---
@bot.message_handler(commands=['status'])
def enviar_status(message):
    bot.reply_to(message, "✅ Bot online e vigiando os ingressos!")

# Iniciar servidor fantasma para o Render não dar erro de 'No open ports'
threading.Thread(target=rodar_servidor_fantasma, daemon=True).start()

# Iniciar monitoramento
threading.Thread(target=checar_sites, daemon=True).start()

print("Bot iniciado com sucesso!")
bot.infinity_polling()
