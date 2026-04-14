# Name: tg_summary.py
# Version: 1.3.4
# Description: Verhindert Halluzinationen/Endlosschleifen durch Stop-Parameter.
# Last Update: 2026-04-14

import asyncio
import requests
import os
import sys
import time
import re
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl.types import PeerChannel, PeerUser, PeerChat

VERSION = "1.3.4"

def load_config(file_path="conf.txt"):
    config = {'targets': []}
    if not os.path.exists(file_path):
        print(f"FEHLER: {file_path} fehlt!"); sys.exit(1)
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            if "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
            else:
                config['targets'].append(line.strip())
    return config

cfg = load_config()
LOG_DIR = cfg.get("LOG_DIR", "summaries")

def save_local_markdown(chat_title, summary):
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    clean_title = re.sub(r'[^\w\s-]', '', chat_title).strip().replace(' ', '_')
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    file_path = os.path.join(LOG_DIR, f"{timestamp}_{clean_title}.md")
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# Digest: {chat_title}\n\n")
            f.write(f"**Zeitpunkt:** {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
            f.write(f"**Modell:** {cfg.get('OLLAMA_MODEL')}\n\n---\n\n")
            f.write(summary)
            f.write("\n\n---\n#EOF")
    except Exception as e:
        print(f"[FEHLER] Schreibfehler: {e}")

async def send_safe_message(client, entity, text):
    MAX_LEN = 4000 
    if len(text) <= MAX_LEN:
        await client.send_message(entity, text)
    else:
        parts = [text[i:i+MAX_LEN] for i in range(0, len(text), MAX_LEN)]
        for i, part in enumerate(parts):
            await client.send_message(entity, f"(Teil {i+1}/{len(parts)})\n{part}")
            await asyncio.sleep(1)

async def resolve_target(client, target_input):
    target_input = str(target_input).strip()
    try:
        if target_input.replace('-', '').isdigit():
            t_id = int(target_input)
            if str(t_id).startswith("-100"):
                return await client.get_entity(PeerChannel(int(str(t_id).replace("-100", ""))))
            elif str(t_id).startswith("-"):
                return await client.get_entity(PeerChat(abs(t_id)))
            else:
                return await client.get_entity(PeerUser(t_id))
        return await client.get_entity(target_input)
    except Exception:
        return None

async def process_chat(client, entity, hours, ollama_url, model):
    chat_title = getattr(entity, 'title', getattr(entity, 'first_name', 'Unbekannt'))
    print(f"\n[STEP 1] Lese Chat: {chat_title}")
    
    time_limit = datetime.now() - timedelta(hours=hours)
    history = ""
    async for msg in client.iter_messages(entity, offset_date=time_limit, reverse=True):
        if msg.text:
            sender = await msg.get_sender()
            name = getattr(sender, 'first_name', 'User')
            history += f"[{msg.date.strftime('%H:%M')}] {name}: {msg.text}\n"
    
    if not history: return None

    print(f"[STEP 2] KI-Verarbeitung ({model})...")
    timeout_val = int(cfg.get("OLLAMA_TIMEOUT", 300))
    start_time = time.time()
    
    try:
        # Erhöhte Stabilität durch Stop-Tokens und Predict-Limit
        resp = requests.post(f"{ollama_url}/api/generate", json={
            "model": model,
            "prompt": f"Fasse diesen Chat kurz zusammen. Beende die Antwort sofort nach der Zusammenfassung. Generiere keine neuen User-Nachrichten!\n\nChatverlauf:\n{history}",
            "stream": False,
            "options": {
                "num_predict": 800,       # Harte Grenze für die Länge (gegen Endlosschleifen)
                "temperature": 0.2,       # Weniger Kreativität = stabiler
                "stop": ["<|endoftext|>", "<|im_start|>", "user:", "User:"] # Stoppt bei diesen Zeichen
            }
        }, timeout=timeout_val)
        
        if resp.status_code == 200:
            summary = resp.json().get('response').strip()
            duration = round(time.time() - start_time, 2)
            print(f"[OK] KI fertig ({duration}s).")
            save_local_markdown(chat_title, summary)
            return f"📊 **Digest: {chat_title}**\n\n" + summary
    except Exception as e:
        print(f"[FEHLER] {e}")
    return None

async def main():
    print(f"--- TG-Multi-Summarizer v{VERSION} ---")
    session = os.path.join(os.path.dirname(__file__), 'ubot_tg_session')
    targets = cfg.get('targets', [])
    delivery_target = cfg.get("SUMMARY_DELIVERY_CHAT")
    
    async with TelegramClient(session, cfg.get("API_ID"), cfg.get("API_HASH")) as client:
        delivery_entity = await resolve_target(client, delivery_target)
        if not delivery_entity: return

        for t in targets:
            entity = await resolve_target(client, t)
            if entity:
                digest = await process_chat(
                    client, 
                    entity, 
                    int(cfg.get("HOURS", 24)), 
                    cfg.get("OLLAMA_BASE_URL"), 
                    cfg.get("OLLAMA_MODEL")
                )
                if digest:
                    await send_safe_message(client, delivery_entity, digest)
                await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())

#EOF
