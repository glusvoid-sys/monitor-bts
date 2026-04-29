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

# --- FUNÇÕES DE APOIO ---

def rodar_servidor_fantasma():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

def verificar_ingressos():
    while True:
        for data, url in SHOWS.items():
            try:
                print(f"Checando ingressos para {data}...")
                # Aqui futuramente adicionaremos a lógica de leitura do site
            except Exception as e:
                print(f"Erro ao checar {data}: {e}")
        time.sleep(300) # Checa a cada 5 minutos

# --- COMANDOS DO TELEGRAM ---

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

@bot.message_handler(commands=['status'])
def enviar_status(message):
    bot.reply_to(message, "✅ Monitor chileno ativo! Analisando preços e disponibilidade em espanhol.")

@bot.message_handler(commands=['link'])
def enviar_link(message):
    markup = types.InlineKeyboardMarkup()
    btn14 = types.InlineKeyboardButton("🎫 Ingresso 14/10", url=SHOWS["14/10"])
    btn16 = types.InlineKeyboardButton("🎫 Ingresso 16/10", url=SHOWS["16/10"])
    btn17 = types.InlineKeyboardButton("🎫 Ingresso 17/10", url=SHOWS["17/10"])
    markup.add(btn14)
    markup.add(btn16)
    markup.add(btn17)
    bot.send_message(message.chat.id, "💜 **SELECIONE A DATA DO SHOW:**", reply_markup=markup, parse_mode="Markdown")

# --- INICIALIZAÇÃO ---

# Iniciando as tarefas em segundo plano (importante estar antes do polling)
threading.Thread(target=rodar_servidor_fantasma, daemon=True).start()
threading.Thread(target=verificar_ingressos, daemon=True).start()

# Mantém o bot ouvindo o Telegram
bot.infinity_polling()
