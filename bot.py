
import telebot
from collections import deque
from config import (
    TELEGRAM_TOKEN,
    OPENROUTER_TOKEN,
    OPENROUTER_MODEL,
    OPENROUTER_URL,
    EVARISTINHO_MAX_HISTORICO,
    EVARISTINHO_SYSPROMPT
)   
from openrouter import OpenRouter
from utils import _typing_action

class HackerSpaceBot:
    def __init__(self):
        self.bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode="Markdown")
        self.username = f"@{self.bot.get_me().username}"
        
        print(f"🤖 Bot inicializado como: {self.username}")
        
        self.ai = OpenRouter(OPENROUTER_TOKEN, OPENROUTER_URL, OPENROUTER_MODEL)
        self._register_handlers()
        self.msg_historico = {}
        
    def _get_context_key(self, message):
        """Chave única para isolar as mensagens por chat e tópico."""
        thread_id = getattr(message, 'message_thread_id', None)
        return (message.chat.id, thread_id)
    
    def _register_handlers(self):
        self.bot.register_message_handler(self._link_afiliado, commands=['links', 'Links', 'LINKS'])
        self.bot.register_message_handler(self._limpar_memoria, commands=['limpar', 'reset'])
        self.bot.register_message_handler(
            self._handle_ai, 
            func=lambda msg: msg.text and (
                msg.text.startswith(('/evaristinho')) or 
                self.username.lower() in msg.text.lower()
            )
        )
        self.bot.register_message_handler(
            self._processar_mensagem, 
            func=lambda msg: bool(msg.text)
        )

    def _limpar_memoria(self, message):
        with _typing_action(self.bot, message.chat.id):
            key = self._get_context_key(message)
            if key in self.msg_historico:
                self.msg_historico[key].clear()
                self.bot.reply_to(message, "🧠 Histórico recente deste tópico foi zerado!")
            else:
                self.bot.reply_to(message, "Não há mensagens salvas neste canal.")

    def _link_afiliado(self, message):
        with _typing_action(self.bot, message.chat.id):
            self.bot.reply_to(message, "Em breve eu te conto!")

    def _processar_mensagem(self, message):
        """Apenas grava o texto de qualquer usuário na memória."""
        context_key = self._get_context_key(message)
        
        if context_key not in self.msg_historico:
            self.msg_historico[context_key] = deque(maxlen=EVARISTINHO_MAX_HISTORICO)
            
        usuario = message.from_user.first_name or "Membro"
        
        # Adiciona a mensagem atual do usuário na fila
        self.msg_historico[context_key].append({
            "user": usuario, 
            "text": message.text.strip()
        })
        print(f"mensagem recebida: {message.text.strip()}")

    def _handle_ai(self, message):
        """Processa a mensagem quando a IA é chamada."""
        self._processar_mensagem(message)
        
        context_key = self._get_context_key(message)
        user_name = message.from_user.first_name or "Companheiro"
        system_prompt = EVARISTINHO_SYSPROMPT.format(user_name=user_name)
        
        prompt = message.text
        for cmd in ['/run', '/ia', '/evaristinho', self.username, self.username.lower()]:
            prompt = prompt.replace(cmd, "")
        prompt = prompt.strip()

        if not prompt:
            self.bot.reply_to(message, "⚠️ Mande uma instrução junto com o comando/menção!")
            return
        
        prompt_com_contexto = "--- Histórico das últimas mensagens do tópico/grupo ---\n"
        for item in self.msg_historico[context_key]:
            prompt_com_contexto += f"{item['user']}: {item['text']}\n"
        prompt_com_contexto += "--- Fim do histórico ---\n\n"
        prompt_com_contexto += f"Instrução atual de {user_name}: {prompt if prompt else message.text}"
        
        print('\n')
        print(prompt_com_contexto)
        print('\n')
        try:
            
            with _typing_action(self.bot, message.chat.id):
                response = self.ai.chat(prompt_com_contexto, system_prompt)
                self.msg_historico[context_key].append({
                    "user": "Assistente (Você)", 
                    "text": response
                })
                self.bot.reply_to(message, response)
        except Exception as e:
            self.bot.reply_to(message, f"❌ Erro no nó da IA: `{e}`", parse_mode="Markdown")

    def run(self):
        print("⚡ Hacker Space Bot (OpenRouter Ready) iniciado...")
        self.bot.infinity_polling(
            timeout=10, 
            long_polling_timeout=5
        )


if __name__ == "__main__":
    hacker_bot = HackerSpaceBot()
    hacker_bot.run()