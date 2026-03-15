#!/usr/bin/env python3
"""
scorcy.py — Entry point di Scorcy (Linux).
Rileva la modalità di avvio e delega a ui_gui, ui_terminal o core.
Non contiene logica applicativa né codice UI.

Utilizzo:
  python3 scorcy.py                              → GUI (se tkinter disponibile)
  python3 scorcy.py --terminal                   → terminale interattivo
  python3 scorcy.py -icons                       → apre la cartella icone
  python3 scorcy.py "YouTube" "https://..."      → inline, browser predefinito
  python3 scorcy.py "YouTube" "https://..." "y.png"            → inline con icona
  python3 scorcy.py "YouTube" "https://..." "y.png" "brave"    → inline con browser
  python3 scorcy.py -f "YouTube" "https://..."                 → sovrascrive senza chiedere
"""

import sys
import core


# ══════════════════════════════════════════════════════════════
# PARTE 1 — HELP
# Stampa il riepilogo di tutti i comandi disponibili con
# esempi concreti. Mostra anche i browser rilevati sulla
# macchina corrente, così l'utente sa quali nomi usare
# nell'argomento browser. Il flag -f è documentato nella
# sezione inline.
# ══════════════════════════════════════════════════════════════

def _mostra_help():
    nomi_browser = [n for n, _ in core.BROWSER_DISPONIBILI]
    browser_lista = (
        "Browser rilevati: " + ", ".join(nomi_browser)
        if nomi_browser else
        "⚠️  Nessun browser rilevato sulla macchina"
    )
    print(f"""
┌──────────────────────────────────┐
│   Scorcy — Crea Scorciatoie Web  │
└──────────────────────────────────┘

  python3 scorcy.py    GUI — richiede tkinter, altrimenti parte il terminale
  --terminal  -t       Terminale interattivo
  -icons  -i           Apre la cartella icone ({core.ICONS_PATH})
  --help  -h           Mostra questo messaggio

  "Nome" "URL"                        Crea scorciatoia inline
  "Nome" "URL" "icona.png"            Con icona personalizzata
  "Nome" "URL" "icona.png" "browser"  Con browser specifico
  -f "Nome" "URL" ...                 Sovrascrive senza chiedere conferma

{browser_lista}
""")


# ══════════════════════════════════════════════════════════════
# PARTE 2 — MODALITÀ INLINE
# Attivata quando vengono passati almeno nome e URL come
# argomenti. Il browser è opzionale: se passato viene cercato
# per nome parziale tra i browser disponibili.
# Il parametro forza, attivato dal flag -f nel routing,
# chiama sovrascrivi_scorciatoia senza chiedere conferma
# invece di lanciare FileExistsError.
# ══════════════════════════════════════════════════════════════

def _modalita_inline(nome: str, url: str, icona: str = "",
                     browser_hint: str = "", forza: bool = False):
    browser_exe = ""
    if browser_hint:
        hint = browser_hint.lower()
        browser_exe = next(
            (exe for n, exe in core.BROWSER_DISPONIBILI if hint in n.lower()),
            ""
        )
        if not browser_exe:
            print(f"⚠️  Browser '{browser_hint}' non trovato, uso predefinito.")

    try:
        if forza:
            s      = core.sovrascrivi_scorciatoia(nome, url, icona, browser_exe)
            azione = "sovrascritta"
        else:
            s      = core.crea_scorciatoia(nome, url, icona, browser_exe)
            azione = "creata"
        print(f"✅ Scorciatoia {azione}: {s.percorso}")
        print(f"   → URL:     {s.url}")
        print(f"   → Browser: {s.nome_browser}")
        print(f"   → Icona:   {s.icon_path}")
    except FileExistsError:
        nome_file = core.nome_a_filename(nome)
        print(f"⚠️  Esiste già '{nome_file}'. Usa -f per sovrascrivere.")


# ══════════════════════════════════════════════════════════════
# PARTE 3 — ROUTING
# Legge sys.argv e smista verso la modalità corretta.
# Ordine di priorità:
#   1. --help
#   2. inline (≥ 2 argomenti posizionali), con -f opzionale
#   3. sottocomando icone
#   4. flag --terminal
#   5. GUI (default, con fallback automatico al terminale)
# Il flag -f viene estratto prima di leggere gli argomenti
# posizionali, così può stare in qualsiasi posizione nella
# riga di comando (es. sia "-f Nome URL" che "Nome URL -f").
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    args = sys.argv[1:]

    # Help
    if any(a in args for a in ("--help", "-h")):
        _mostra_help()
        sys.exit(0)

    # Estrai -f e rimuovilo dagli args posizionali
    forza = "-f" in args
    args  = [a for a in args if a != "-f"]

    # Modalità inline: almeno nome e URL
    if len(args) >= 2 and not args[0].startswith("-"):
        nome         = args[0]
        url          = args[1]
        icona        = args[2] if len(args) >= 3 else ""
        browser_hint = args[3] if len(args) >= 4 else ""
        _modalita_inline(nome, url, icona, browser_hint, forza)
        sys.exit(0)

    # Sottocomando: apre cartella icone
    if any(a in args for a in ("-icons", "-i")):
        core.apri_cartella_icone()
        print(f"📂 Cartella icone aperta: {core.ICONS_PATH}")
        sys.exit(0)

    # Modalità terminale esplicita
    if any(a in args for a in ("--terminal", "-t")):
        import ui_terminal
        ui_terminal.avvia()
        sys.exit(0)

    # Default: GUI con fallback automatico al terminale
    try:
        import tkinter  # noqa: F401 — solo per verificare disponibilità
        import ui_gui
        ui_gui.avvia()
    except ImportError:
        print("⚠️  tkinter non disponibile. Avvio modalità terminale...")
        import ui_terminal
        ui_terminal.avvia()
