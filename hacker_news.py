import json
import time
import feedparser
import telebot
from utils import _typing_action

from openrouter import OpenRouter
from config import (
    HACKE_NEWS_RSS_FEEDS,
    HACKE_NEWS_PROMPT,
    OPENROUTER_TOKEN,
    OPENROUTER_URL,
    OPENROUTER_MODEL,
    TELEGRAM_CHAT_ID,
    TELEGRAM_TOPIC_ID,
    TELEGRAM_TOKEN
)


class HackerNews:
    
    def __init__(self):
        self.bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode="Markdown")
        self.ai = OpenRouter(OPENROUTER_TOKEN, OPENROUTER_URL, OPENROUTER_MODEL)
    
    def buscar_noticias_rss(self) -> list:
        todas_noticias = []
        
        for url in HACKE_NEWS_RSS_FEEDS:
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:3]:
                data_publicacao = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
                
                timestamp = time.mktime(data_publicacao) if data_publicacao else 0

                todas_noticias.append({
                    "title": entry.title,
                    "summary": getattr(entry, "summary", ""),
                    "link": entry.link,
                    "timestamp": timestamp
                })

        todas_noticias.sort(key=lambda item: item["timestamp"], reverse=True)

        for noticia in todas_noticias:
            noticia.pop("timestamp", None)

        return todas_noticias

    def resumir_com_ai(self, noticias: list) -> str:
        prompt = HACKE_NEWS_PROMPT.format(noticias=json.dumps(noticias[:15], ensure_ascii=False))
        return self.ai.chat(prompt)

    def envia_para_grupo(self, resumo: str):
        mensagem_final = (
            f"🚨 **TOP 5 NOTÍCIAS RED TEAM DO DIA** 🚨\n\n"
            f"{resumo}"
        )

        self.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=mensagem_final,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            message_thread_id=int(TELEGRAM_TOPIC_ID) if TELEGRAM_TOPIC_ID else None
        )
    
    def run(self):
        with _typing_action(self.bot, TELEGRAM_CHAT_ID):
            print("Coletando notícias via RSS...")
            noticias = self.buscar_noticias_rss()
            
            print("Filtrando e resumindo com IA (OpenRouter)...")
            resumo_ia = self.resumir_com_ai(noticias)
            if 'Aconteceu algum erro e não consegui retornar a resposta.' in resumo_ia:
                resumo_ia = self.resumir_com_ai(noticias)
            
            print("Enviando para o tópico do Telegram...")
            self.envia_para_grupo(resumo_ia)
            print("Envio concluído com sucesso!")


if __name__ == "__main__":
    hn = HackerNews()
    hn.run()