import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import time
import os
import threading
import http.server
import socketserver

# --- CONFIGURAÇÕES ---
TOKEN = os.environ.get('TELEGRAM_TOKEN')
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

@bot.message_handler(commands=['start'])
def enviar_boas_vindas(message):
    texto = (
        "✨ **Bem-vinda ao Monitor de Ingressos BTS Chile!** ✨\n\n"
        "Estou aqui para te ajudar a garantir seu lugar no show. "
        "Vou monitorar os links da Ticketmaster e te avisar se algo mudar!\n\n"
        "📌 **Comandos disponíveis:**\n"
        "/link - Abre os botões com os links de compra\n"
        "/status - Verifica se o monitor está rodando agora"
    )
    bot.reply_to(message, texto, parse_mode="Markdown")
@bot.message_handler(commands=['link'])
def enviar_link(message):
    markup = types.InlineKeyboardMarkup()
    # Criando os botões para cada data
    btn14 = types.InlineKeyboardButton("🎫 Ingresso 14/10", url="https://www.ticketmaster.cl/event/bts-world-tour-arirang-live-2026-scl-venta-general-14-de-octubre")
    btn16 = types.InlineKeyboardButton("🎫 Ingresso 16/10", url="https://www.ticketmaster.cl/event/bts-world-tour-arirang-live-2026-scl-venta-general-16-de-octubre")
    btn17 = types.InlineKeyboardButton("🎫 Ingresso 17/10", url="https://www.ticketmaster.cl/event/bts-world-tour-arirang-live-2026-scl-venta-general-17-de-octubre")
    
    markup.add(btn14)
    markup.add(btn16)
    markup.add(btn17)
    
    bot.send_message(message.chat.id, "💜 **SELECIONE A DATA DO SHOW:**", reply_markup=markup, parse_mode="Markdown")
threading.Thread(target=rodar_servidor_fantasma, daemon=True).start()
threading.Thread(target=verificar_ingressos, daemon=True).start()
bot.infinity_polling()


def verificar_ingressos():
    while True:
        for data, url in SHOWS.items():
            # Aqui o bot vai "visitar" o site silenciosamente
            # Se ele detectar mudança, ele te envia mensagem
            print(f"Checando ingressos para {data}...")
            # (Lógica de busca aqui)
        time.sleep(300) # Espera 5 minutos para checar de novo
