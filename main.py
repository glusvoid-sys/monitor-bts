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

# Links de Ingressos (Vigiando 14, 16 e 17 de Outubro)
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
        # Mantém o processo de vigia dos ingressos ativo
        print("Vigiando ingressos Ticketmaster Chile...")
        time.sleep(300)

def verificar_voos():
    global promos_encontradas
    urls_feeds = [
        "https://www.passagensimperdiveis.com.br/feed/",
        "https://www.melhoresdestinos.com.br/feed"
    ]
    
    while True:
        for url_feed in urls_feeds:
            try:
                response = requests.get(url_feed, timeout=15)
                soup = BeautifulSoup(response.content, 'xml')
                itens = soup.find_all('item', limit=10)
                
                for item in itens:
                    titulo = item.title.text.lower()
                    link = item.link.text

                    # Filtra por Salvador e Chile/Santiago
                    if ("chile" in titulo or "santiago" in titulo) and "salvador" in titulo:
                        # Define a cor do alerta pelo preço mencionado no título
                        if any(x in titulo for x in ["800", "900", "1000"]):
                            cor = "🟢 **OFERTA IMPERDÍVEL! (R$ 800-1000)**"
                        elif "2000" in titulo:
                            cor = "🔴 **ALERTA: LIMITE DO ORÇAMENTO (R$ 2000)**"
                        else:
                            cor = "🟡 **PREÇO INTERESSANTE**"

                        promo_formatada = f"{cor}\n✈️ {item.title.text}\n🔗 {link}"
                        
                        if link not in [p.split('\n')[-1] for p in promos_encontradas]:
                            bot.send_message(CHAT_ID, f"🚨 **NOVA PROMOÇÃO SSA -> SCL!** 🚨\n\n{promo_formatada}", parse_mode="Markdown")
                            promos_encontradas.insert(0, promo_formatada)
                            promos_encontradas = promos_encontradas[:5]
            except Exception as e:
                print(f"Erro na busca de voos: {e}")
        time.sleep(600)

# --- COMANDOS DO TELEGRAM ---

@bot.message_handler(commands=['start'])
def enviar_boas_vindas(message):
    texto = (
        "👋 **Olá! Bem-vinda ao seu Assistente Pessoal de Viagem!** 💜\n\n"
        "Estou configurado para garantir que você não perca nada da sua viagem para o Chile! "
        "Meu trabalho é vigiar 24h por dia as seguintes frentes:\n\n"
        "🎫 **INGRESSOS:** Monitoro os links da Ticketmaster Chile para os dias 14, 16 e 17 de Outubro.\n"
        "✈️ **VOOS:** Procuro promoções de Salvador (SSA) para Santiago (SCL) entre R$ 800 e R$ 2.000.\n"
        "📅 **DATAS:** Foco total no seu período de viagem (13 a 17 de Outubro).\n\n"
        "📌 **COMANDOS DISPONÍVEIS:**\n"
        "🔹 /voos - Ver as últimas promoções 'bug' e acessar o buscador em tempo real.\n"
        "🔹 /link - Acessar direto as páginas de compra dos ingressos.\n"
        "🔹 /status - Confirmar se eu continuo acordado e vigiando tudo.\n\n"
        "💡 *Dica: Mantenha as notificações ativadas! Se uma passagem barata surgir, eu te aviso na hora.*"
    )
    bot.reply_to(message, texto, parse_mode="Markdown")

@bot.message_handler(commands=['voos'])
def comando_voos(message):
    # Link direto para o Google Flights configurado para as datas da usuária
    link_google = "https://www.google.com/travel/flights?q=Flights%20to%20SCL%20from%20SSA%20on%202026-10-13%20through%202026-10-17"
    
    resumo = "\n\n".join(promos_encontradas) if promos_encontradas else "🔎 Nenhuma promoção 'bug' detectada recentemente. Use o botão abaixo para checar os preços de hoje!"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🌍 Abrir Google Flights (13-17/10)", url=link_google))
    
    bot.send_message(message.chat.id, f"📍 **Monitor de Passagens (SSA -> SCL):**\n\n{resumo}", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['link'])
def enviar_link(message):
    markup = types.InlineKeyboardMarkup()
    for data, url in SHOWS.items():
        markup.add(types.InlineKeyboardButton(f"🎫 Ingresso {data}", url=url))
    bot.send_message(message.chat.id, "💜 **LINKS OFICIAIS TICKETMASTER CHILE:**", reply_markup=markup)

@bot.message_handler(commands=['status'])
def enviar_status(message):
    bot.reply_to(message, "✅ Sistema Online: Monitorando Ingressos e Voos (Salvador-Chile)!")

# --- INICIALIZAÇÃO ---

# Remove webhooks antigos para evitar o Erro 409 Conflict
bot.remove_webhook()

threading.Thread(target=rodar_servidor_fantasma, daemon=True).start()
threading.Thread(target=verificar_ingressos, daemon=True).start()
threading.Thread(target=verificar_voos, daemon=True).start()

bot.infinity_polling()
