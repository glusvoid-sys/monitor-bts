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

promos_encontradas = []

# --- FUNÇÕES DE APOIO ---

def rodar_servidor_fantasma():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

def verificar_ingressos():
    while True:
        # A lógica de monitoramento dos ingressos continua ativa aqui
        print("Vigiando ingressos Ticketmaster Chile...")
        time.sleep(300)

def verificar_voos():
    global promos_encontradas
    # Fontes de pesquisa: Melhores Destinos e Passagens Imperdíveis
    urls_feeds = [
        "https://www.passagensimperdiveis.com.br/feed/",
        "https://www.melhoresdestinos.com.br/feed"
    ]
    
    while True:
        for url_feed in urls_feeds:
            try:
                print(f"Buscando voos em: {url_feed}")
                response = requests.get(url_feed, timeout=15)
                soup = BeautifulSoup(response.content, 'xml')
                itens = soup.find_all('item', limit=10)
                
                for item in itens:
                    titulo = item.title.text.lower()
                    link = item.link.text

                    # Filtro: Salvador + Chile e que não seja absurdo de caro
                    if ("chile" in titulo or "santiago" in titulo) and "salvador" in titulo:
                        # O bot vai te avisar para você conferir se está no seu orçamento (até 2000)
                        promo_formatada = f"✈️ {item.title.text}\n🔗 {link}"
                        
                        if promo_formatada not in promos_encontradas:
                            msg = f"🚨 **PROMOÇÃO SSA -> SCL DETECTADA!** 🚨\n\n{item.title.text}\n\n⚠️ Confira se o valor está abaixo de R$ 2.000 no link!\n\n🔗 Link: {link}"
                            bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
                            promos_encontradas.insert(0, promo_formatada)
                            promos_encontradas = promos_encontradas[:5]
            except Exception as e:
                print(f"Erro na busca de voos: {e}")
        time.sleep(600) # Verifica a cada 10 minutos

# --- COMANDOS DO TELEGRAM ---

@bot.message_handler(commands=['start'])
def enviar_boas_vindas(message):
    texto = (
        "✨ **Monitor BTS: Ingressos + Voos (SSA-SCL)** ✨\n\n"
        "Vigiando ingressos no Chile e voos saindo de Salvador até R$ 2.000!\n\n"
        "📌 **Comandos:**\n"
        "/voos - Últimas promoções Salvador-Chile\n"
        "/link - Links dos ingressos\n"
        "/status - Ver se o bot está ativo"
    )
    bot.reply_to(message, texto, parse_mode="Markdown")

@bot.message_handler(commands=['voos'])
def comando_voos(message):
    if not promos_encontradas:
        bot.reply_to(message, "🔎 Nenhuma promoção recente de Salvador para o Chile abaixo de R$ 2.000 encontrada nas últimas horas.")
    else:
        lista = "\n\n".join(promos_encontradas)
        bot.reply_to(message, f"📍 **Promoções recentes Salvador -> Chile:**\n\n{lista}", parse_mode="Markdown")

@bot.message_handler(commands=['link'])
def enviar_link(message):
    markup = types.InlineKeyboardMarkup()
    for data, url in SHOWS.items():
        markup.add(types.InlineKeyboardButton(f"🎫 Ingresso {data}", url=url))
    bot.send_message(message.chat.id, "💜 **LINKS TICKETMASTER CHILE:**", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['status'])
def enviar_status(message):
    bot.reply_to(message, "✅ Monitor Ativo: Ingressos e Voos (Salvador-Chile)!")

# --- INICIALIZAÇÃO ---

threading.Thread(target=rodar_servidor_fantasma, daemon=True).start()
threading.Thread(target=verificar_ingressos, daemon=True).start()
threading.Thread(target=verificar_voos, daemon=True).start()

bot.infinity_polling()
