# Babbel-Brief

🇩🇪 Deutsch: Beschreibung

Name: Babbel-Brief
Vibe: Effizient, bodenständig, informativ.

    Was ist der Babbel-Brief?
    Der Babbel-Brief ist mein persönlicher KI-Sekretär für Telegram. Er liest automatisch definierte Chats und Kanäle aus, filtert das „Gebabbel“ heraus und liefert täglich eine prägnante Zusammenfassung der wichtigsten Themen direkt in meinen Log-Kanal.

    Wie es funktioniert:
    Basierend auf der Telethon-API extrahiert ein Python-Skript (auf meinem Orange Pi) die Nachrichten der letzten 24 Stunden. Diese werden verschlüsselt an meine lokale KI (Ollama auf einem Ryzen 5/RTX 5060) gesendet, dort analysiert und als strukturierter Digest aufbereitet. Das Ergebnis dient nicht nur der schnellen Übersicht, sondern wird als Markdown-Archiv direkt in mein Docmost-System gepumpt, um als Langzeitgedächtnis für mein persönliches RAG-System (KI-Experte) zur Verfügung zu stehen.

Wirf einen Blick auf die api-guide.txt damit du deinen eigenen Key bekommen kannst !!


🇺🇸 English: Description

Name: Babbel-Brief (The "Chatter Digest")
Vibe: Professional, automated, insightful.

    What is Babbel-Brief?
    Babbel-Brief is a custom AI-driven assistant designed to summarize Telegram conversations. It acts as a bridge between high-volume group chats and a structured personal knowledge base, distilling daily chatter into actionable insights.

    Technical Workflow:
    Running as a cronjob on a local Orange Pi, the script utilizes the Telethon API to fetch the last 24 hours of messages from selected targets. The raw text is then processed by a local LLM (Ollama) running on high-efficiency hardware. The generated summaries are delivered via Telegram and simultaneously archived in Docmost. This creates a continuous data pipeline for a RAG-based (Retrieval-Augmented Generation) AI expert that knows exactly what was discussed in my private communities.

##take a look to the api-guide.txt to get your codes !


Powerd by AI .-)
