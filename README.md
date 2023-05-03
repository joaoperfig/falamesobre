# Fala-me sobre

Agentes GPT peritos em tópicos niche com contexto obtido no arquivo.pt

## Instalação Local:

Clone o git e instale os requisitos com:

```
git clone https://github.com/joaoperfig/falamesobre
cd falamesobre
pip3 install -r requirements.txt
```
Para correr a api é necessário uma API key do chatGPT, obtenha uma em https://platform.openai.com/account/api-keys (ou peça uma ao João). E coloque a key em __secrets.txt__.  
Lance a api com:
```
python3 -m uvicorn api:app
```
Pode mudar a porta em que a api corre com __--port__

Para aceder à interface, abra __interface/index.html__
