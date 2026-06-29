import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("MTUyMDk1MTUyMzM5ODM4NTc3NA.GOxqxn.wusX2RdOjpaI-uAmP37fDYYFUaXCURICqg6NaM")
GUILD_ID = int(os.getenv("1520112650392961226"))           # ID del server (guild)
TICKET_CATEGORY_ID = int(os.getenv("1520112650875437099"))  # ID della categoria dove creare i ticket
SUPPORT_ROLE_ID = int(os.getenv("1520951171676635247")) # (opzionale) ID del ruolo staff
