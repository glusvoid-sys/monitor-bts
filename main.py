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

historico_setores = {data: "" for data in SHOWS}

def rodar_servidor_fantasma():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

def checar_sites():
    while True:
        for data, url in SHOWS.items():
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                res = requests.get(url, headers=headers, timeout=15)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # BUSCA EM ESPANHOL (O que o site diz)
                conteudo_util = ""
                for elemento in soup.find_all(['span', 'div', 'td', 'button']):
                    texto = elemento.get_text().strip().lower()
                    # Procurando termos chaves do site chileno
                    if "$" in texto or "disponib" in texto or "selecciona" in texto or "precio" in texto:
                        conteudo_util += texto + " | "

                if historico_setores[data] != "" and conteudo_util != historico_setores[data]:
                    # RESPOSTA EM PORTUGUÊS (O que você lê)
                    msg = (
                        f"🚨 **ALTERAÇÃO NO TICKETMASTER CHILE!**\n"
                        f"📅 **Data do Show:** {data}\n\n"
                        f"O bot detectou mudanças nos setores, preços ou botões de compra.\n"
                        f"🔗 Confira aqui: {url}"
                    )
                    bot.send_message(CHAT_ID, msg)
                
                historico_setores[data] = conteudo_util
            except Exception as e:
                print(f"Erro no monitor: {e}")
            time.sleep(15)
        time.sleep(180)

@bot.message_handler(commands=['status'])
def enviar_status(message):
    bot.reply_to(message, "✅ Monitor chileno ativo! Analisando preços e disponibilidade em espanhol.")

threading.Thread(target=rodar_servidor_fantasma, daemon=True).start()
threading.Thread(target=checar_sites, daemon=True).start()
bot.infinity_polling()
