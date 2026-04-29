import telebot
import requests
from bs4 import BeautifulSoup
import time
import os
import threading

# --- CONFIGURAÇÕES ---
TOKEN = "8711199299:AAFWLWO6s5hwbuC9tTkU4KKVOuwV4255cgg"
CHAT_ID = "8121263752"  # Seu ID inserido aqui
bot = telebot.TeleBot(TOKEN)

SHOWS = {
    "14/10": "https://www.ticketmaster.cl/event/bts-world-tour-arirang-live-2026-scl-venta-general-14-de-octubre",
    "16/10": "https://www.ticketmaster.cl/event/bts-world-tour-arirang-live-2026-scl-venta-general-16-de-octubre",
    "17/10": "https://www.ticketmaster.cl/event/bts-world-tour-arirang-live-2026-scl-venta-general-17-de-octubre"
}

# Histórico para comparar mudanças
historico_texto = {data: "" for data in SHOWS}

def checar_sites():
    while True:
        for data, url in SHOWS.items():
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                res = requests.get(url, headers=headers, timeout=15)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # Pegamos o texto limpo da página para detectar qualquer mudança (preço, setor, etc)
                texto_atual = soup.get_text()

                if historico_texto[data] != "" and texto_atual != historico_texto[data]:
                    msg = f"🚨 **MUDANÇA DETECTADA NO SITE!**\n\n📅 **Show Dia:** {data}\n\nHouve uma alteração nos setores ou preços. Verifique rápido:\n🔗 {url}"
                    bot.send_message(CHAT_ID, msg)
                    print(f"Alteração enviada para o dia {data}")
                
                historico_texto[data] = texto_atual
            except Exception as e:
                print(f"Erro ao checar {data}: {e}")
            
            time.sleep(10) # Pausa entre as datas
        
        print("Ciclo de vigilância completo. Aguardando 2 minutos...")
        time.sleep(120)

# --- COMANDOS INTERATIVOS ---

@bot.message_handler(commands=['start', 'ajuda'])
def enviar_boas_vindas(message):
    msg = (
        "👋 **Olá! Eu sou seu monitor de ingressos do BTS Chile.**\n\n"
        "Comandos disponíveis:\n"
        "👉 `/status` - Verifica se estou acordado e vigiando.\n"
        "👉 `/link` - Envia os links de compra das 3 datas.\n\n"
        "Se qualquer setor abrir ou o preço mudar, eu te aviso aqui na hora!"
    )
    bot.reply_to(message, msg)

@bot.message_handler(commands=['status'])
def enviar_status(message):
    resposta = "📊 **Status do Monitoramento:**\n"
    for data in SHOWS.keys():
        resposta += f"✅ Dia {data}: Monitorando setores e valores...\n"
    resposta += "\n🕒 Checagem automática a cada 2 minutos."
    bot.send_message(message.chat.id, resposta)

@bot.message_handler(commands=['link'])
def enviar_links(message):
    msg = "🔗 **Links Oficiais (Ticketmaster CL):**\n\n"
    for data, url in SHOWS.items():
        msg += f"📅 {data}: {url}\n\n"
    bot.send_message(message.chat.id, msg)

# Rodar o monitor de sites em uma linha separada
threading.Thread(target=checar_sites, daemon=True).start()

# Rodar o bot para responder seus comandos
print("Bot online e aguardando comandos...")
bot.infinity_polling()
