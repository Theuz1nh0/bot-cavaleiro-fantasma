from dotenv import load_dotenv
import os
import json

ARQUIVOS_CONFIG = "config.json"

# 🧩 Carrega o arquivo de configuração
def carregar_config():
    if not os.path.exists(ARQUIVOS_CONFIG):
        return {"canais_para_aviso": []}
    with open(ARQUIVOS_CONFIG, "r") as f:
        return json.load(f)

# 🧩 Salva o arquivo de configuração
def salvar_config(config):
    with open(ARQUIVOS_CONFIG, "w") as f:
        json.dump(config, f, indent=4)

load_dotenv()
TOKEN = os.getenv("TOKEN")