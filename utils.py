import threading
from contextlib import contextmanager

@contextmanager
def _typing_action(bot, chat_id: int):
    """Mantém o status de digitando ativo em segundo plano durante a requisição da IA."""
    stop_event = threading.Event()

    def send_typing():
        print("Respondendo uma pergunta...")
        while not stop_event.is_set():
            try:
                bot.send_chat_action(chat_id=chat_id, action='typing')
            except Exception:
                pass
            # O status 'typing' no Telegram dura 5s, renovamos a cada 4s
            stop_event.wait(4)

    thread = threading.Thread(target=send_typing)
    thread.start()
    try:
        yield
    finally:
        stop_event.set()
        thread.join()