# Name: id-scan.py
# Version: 1.0.9
# Description: Listet die letzten 10 Chats inkl. IDs auf.
# Last Update: 2026-04-14


import asyncio
import os
import sys
from telethon import TelegramClient

VERSION = "1.0.9"

def load_config(file_path="conf.txt"):
    config = {}
    if not os.path.exists(file_path):
        print(f"FEHLER: {file_path} fehlt!"); sys.exit(1)
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            if "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
    return config

cfg = load_config()

async def list_chats():
    print(f"--- TG-Scanner v{VERSION} ---")
    session_name = os.path.join(os.path.dirname(__file__), 'ubot_tg_session')
    
    async with TelegramClient(session_name, cfg.get("API_ID"), cfg.get("API_HASH")) as client:
        print("\nSuche deine letzten 10 aktiven Chats...\n")
        print(f"{'NAME':<30} | {'ID':<15} | {'TYP'}")
        print("-" * 60)
        
        async for dialog in client.iter_dialogs(limit=10):
            name = dialog.name[:28] if dialog.name else "Unbekannt"
            print(f"{name:<30} | {dialog.id:<15} | {type(dialog.entity).__name__}")
        
        print("\nKopiere die ID des Chats (inkl. Minuszeichen) in deine conf.txt")

if __name__ == "__main__":
    asyncio.run(list_chats())

#EOF
