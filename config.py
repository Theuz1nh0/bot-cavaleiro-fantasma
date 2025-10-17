from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")
PREFIX = "."

CANAL_FORMULARIO_ID = os.getenv("CANAL_FORMULARIO_ID")
CANAL_AVISOS_ID = os.getenv("CANAL_AVISOS_ID")