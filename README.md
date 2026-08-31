# Evaristinho

Bot de Telegram para o grupo **Hacker Space**, com duas funções:

1. **Evaristinho** — um assistente de IA com a persona de um "desenvolvedor dinossauro" rabugento, que responde quando é mencionado ou chamado por comando, usando o histórico recente do tópico como contexto.
2. **Hacker News** — um job que lê feeds RSS de cibersegurança, pede à IA uma curadoria com as 5 notícias mais relevantes do dia (traduzidas e resumidas em português) e publica num tópico do grupo.

A IA é servida pela [OpenRouter](https://openrouter.ai) através do SDK da OpenAI.

## Stack

- Python >= 3.13 (`.python-version` fixa 3.13)
- [`uv`](https://docs.astral.sh/uv/) para dependências e lockfile (`uv.lock`)
- [`pyTelegramBotAPI`](https://pytba.readthedocs.io) (`telebot`) para o Telegram
- `openai` apontando para o endpoint da OpenRouter
- `feedparser` para os RSS
- `python-dotenv` para configuração

## Estrutura

| Arquivo | Papel |
| --- | --- |
| [bot.py](bot.py) | `HackerSpaceBot`: handlers do Telegram, memória por tópico e chamada à IA. É o entrypoint do bot. |
| [hacker_news.py](hacker_news.py) | `HackerNews`: coleta RSS, resume com IA e publica no tópico. Entrypoint do job de notícias. |
| [openrouter.py](openrouter.py) | `OpenRouter`: wrapper fino sobre o cliente OpenAI, com tratamento de erro e resposta vazia. |
| [config.py](config.py) | Variáveis de ambiente, prompts de sistema, lista de feeds RSS e constantes. |
| [utils.py](utils.py) | `_typing_action`: context manager que mantém o "digitando…" ativo enquanto a IA responde. |
| [main.py](main.py) | Stub gerado pelo `uv init`. Não é usado — não é o entrypoint. |

## Como rodar

```bash
git clone <repo> && cd Evaristinho
uv sync                 # cria .venv e instala as dependências do uv.lock
cp .env-sample .env     # preencha os tokens
```

Variáveis do `.env` (ver [.env-sample](.env-sample)):

| Variável | Descrição |
| --- | --- |
| `TELEGRAM_TOKEN` | Token do bot, obtido no [@BotFather](https://t.me/BotFather). |
| `OPENROUTER_TOKEN` | Chave de API da OpenRouter. |
| `TELEGRAM_CHAT_ID` | ID do grupo onde o resumo de notícias é publicado (negativo para supergrupos). |
| `TELEGRAM_TOPIC_ID` | ID do tópico dentro do grupo. Opcional — se vazio, a mensagem vai para o tópico geral. |

Rodando:

```bash
uv run bot.py           # bot em long polling, roda continuamente
uv run hacker_news.py   # publica o resumo do dia e encerra (bom para cron)
```

O `hacker_news.py` foi feito para execução agendada; um cron diário é o uso esperado:

```
0 9 * * * cd /caminho/para/Evaristinho && /usr/bin/uv run hacker_news.py
```

## Comandos do bot

| Gatilho | Efeito |
| --- | --- |
| `/evaristinho <texto>` ou mencionar `@<bot>` | Chama a IA com o histórico do tópico como contexto. |
| `/limpar`, `/reset` | Zera o histórico em memória daquele tópico. |
| `/links` | Placeholder — hoje responde "Em breve eu te conto!". |
| qualquer outra mensagem de texto | É apenas gravada no histórico, sem resposta. |

## Como funciona a memória

O histórico **vive só em memória** (`self.msg_historico`, um `dict` de `deque`) e é perdido a cada reinício — não há banco de dados.

A chave de contexto é a tupla `(chat.id, message_thread_id)`, então cada tópico do supergrupo tem seu próprio histórico isolado. O limite é `EVARISTINHO_MAX_HISTORICO` (150 mensagens) em [config.py](config.py); ao estourar, as mais antigas caem pela ponta do `deque`.

## Onde mexer

- **Persona / tom do bot**: `EVARISTINHO_SYSPROMPT` em [config.py](config.py). As regras de formatação ali existem porque o Telegram quebra títulos Markdown e tabelas no celular — mantenha-as ao editar.
- **Curadoria de notícias**: `HACKE_NEWS_PROMPT` e `HACKE_NEWS_RSS_FEEDS` em [config.py](config.py). O prompt exige um formato Markdown exato; alterá-lo muda o visual da mensagem publicada.
- **Modelo de IA**: `OPENROUTER_MODEL` em [config.py](config.py), hoje `"openrouter/free"` (hardcoded, não vem do `.env`).
- **Quantidade de itens por feed**: `feed.entries[:3]` em [hacker_news.py](hacker_news.py); a IA recebe no máximo os 15 mais recentes (`noticias[:15]`).

## Convenções

- Código e mensagens ao usuário em **português**; nomes de métodos internos seguem o mesmo idioma (`_processar_mensagem`, `buscar_noticias_rss`).
- Toda operação que chama a IA é envolvida por `with _typing_action(...)` para o usuário não ficar no vazio.
- Falhas da IA não derrubam o bot: `OpenRouter.chat` captura a exceção e devolve uma string de erro; `_handle_ai` responde o erro no chat.

## Pontos conhecidos para melhorar

Boas primeiras contribuições:

- `OpenRouter.chat` monta uma lista `messages` e depois **a ignora**, passando um literal para a API — o que envia `"role": "system"` com conteúdo vazio quando não há `sys_prompt`.
- `hacker_news.py` retenta o resumo apenas uma vez e detecta a falha comparando strings de erro; um retry com backoff seria mais robusto.
- Não há testes nem CI.
- `main.py` é um stub morto e pode ser removido.
- O histórico some em cada restart; persistir em SQLite resolveria.

## Licença

MIT — ver [LICENSE](LICENSE).
