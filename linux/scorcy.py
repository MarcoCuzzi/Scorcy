#!/usr/bin/env python3
"""
scorcy.py — Entry point di Scorcy (Linux).
Si occupa solo di leggere gli argomenti da riga di comando
e instradare verso la modalità corretta.

Uso:
  python3 scorcy.py                              → GUI
  python3 scorcy.py --terminale                  → terminale interattivo
  python3 scorcy.py "YouTube" "https://..."      → inline
  python3 scorcy.py "YouTube" "https://..." "icona.png"  → inline con icona
"""

import sys
import os
import core


# ══════════════════════════════════════════════════════════════
# PARTE 1 — MODALITÀ INLINE
# Attivata quando vengono passati almeno 2 argomenti
# (nome e URL). Crea la scorciatoia direttamente senza
# interazione, gestendo sovrascrittura con --forza
# e stampando il risultato su stdout.
# ══════════════════════════════════════════════════════════════

def _modalita_inline(nome: str, url: str, icona: str = ""):
    try:
        percorso = core.crea_scorciatoia(nome, url, icona)
        print(f"✅ Scorciatoia creata: {percorso}")
        print(f"   → URL:   {url}")
        print(f"   → Icona: {core.risolvi_icona(icona)}")
    except FileExistsError as e:
        if "--forza" in sys.argv:
            os.remove(str(e))
            percorso = core.crea_scorciatoia(nome, url, icona)
            print(f"✅ Scorciatoia sovrascritta: {percorso}")
        else:
            print(f"⚠️  Esiste già '{core.nome_a_filename(nome)}'.")
            print("   Usa --forza per sovrascrivere.")
            sys.exit(1)


# ══════════════════════════════════════════════════════════════
# PARTE 2 — ROUTING PRINCIPALE
# Legge sys.argv e decide quale modalità avviare:
# - 2+ argomenti → inline
# - --terminale  → terminale interattivo
# - default      → GUI (con fallback automatico a terminale
#                  se tkinter non è installato)
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":

    if len(sys.argv) >= 3:
        icona_arg = sys.argv[3] if len(sys.argv) >= 4 else ""
        _modalita_inline(sys.argv[1], sys.argv[2], icona_arg)
        sys.exit(0)

    if "--terminale" in sys.argv:
        import ui_terminal
        ui_terminal.avvia()

    else:
        try:
            import tkinter
            import ui_gui
            ui_gui.avvia()
        except ImportError:
            print("⚠️  tkinter non disponibile. Avvio modalità terminale...")
            import ui_terminal
            ui_terminal.avvia()
          
