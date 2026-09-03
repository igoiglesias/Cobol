from openai import OpenAI

from config import OPENROUTER_MODEL, OPENROUTER_URL, OPENROUTER_TOKEN


class OpenRouter:
    
    def __init__(
        self,
        openrouter_key: str = OPENROUTER_TOKEN,
        openrouter_url: str = OPENROUTER_URL,
        openrouter_model: str = OPENROUTER_MODEL):

        self.openrouter_model = openrouter_model
        self.ai = OpenAI(
            base_url=openrouter_url,
            api_key=openrouter_key,
            default_headers={
                "HTTP-Referer": "https://youtube.com/@igoriglesias",
                "X-Title": "Hacker Space Telegram Bot"
            }
        )
    
    def chat(self, prompt: str, sys_prompt: str = "") -> str:
        messages = []
        if sys_prompt:
            messages.append({"role": "system", "content": sys_prompt})
            
        messages.append({"role": "user", "content": prompt})
        try: 
            response = self.ai.chat.completions.create(
                model=self.openrouter_model,
                extra_body={
                    "reasoning": {
                        "effort": "medium",   # "xhigh" | "high" | "medium" | "low" | "minimal"
                        "exclude": True,
                    },
                    "models": [self.openrouter_model, "openrouter/free"],
                },
                messages=[
                    {
                        "role": "system",
                        "content": sys_prompt
                    },
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.choices[0].message.content
            
            if not content:
                return "Aconteceu algum erro e não consegui retornar a resposta."
            
            if "User Safety" in content:
                return "Não foi possível retornar uma resposta por motivos de segurança."
            
            return content
        
        except Exception as e:
            print(f"Erro ocorrido na API do OpenRouter: {e}")
            return "Erro ao processar as notícias com IA."