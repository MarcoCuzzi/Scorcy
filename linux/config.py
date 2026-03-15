#!/usr/bin/env python3
"""
config.py — Gestione configurazione persistente di Scorcy (Linux).
Legge e scrive ~/.config/scorcy/config.json.
Importato da core.py, ui_gui.py, ui_terminal.py e scorcy.py.
"""

import json
import os


# ══════════════════════════════════════════════════════════════
# PARTE 1 — PERCORSO E VALORI DEFAULT
# CONFIG_PATH è il file JSON su disco.
# DEFAULT contiene tutti i valori di default dell'applicazione:
# - url_validation:   abilita la validazione sintattica degli URL
# - url_reachability: abilita il controllo raggiungibilità URL (bordo verde/rosso)
# - browser_default:  percorso eseguibile del browser preferito;
#                     stringa vuota significa "usa il primo browser rilevato"
# - icons_path:       cartella da cui caricare le icone personalizzate
# ══════════════════════════════════════════════════════════════

CONFIG_PATH = os.path.expanduser("~/.config/scorcy/config.json")

DEFAULT: dict = {
    "url_validation":     True,
    "url_reachability":   True,
    "name_validation":    True,
    "name_duplicate":     True,
    "icon_check":         True,
    "composite_icon":     True,
    "browser_default":    "",
    "icons_path":         os.path.expanduser("~/Scorcy/Icons"),
}


# ══════════════════════════════════════════════════════════════
# PARTE 2 — CARICAMENTO E SALVATAGGIO
# carica() legge il file JSON e lo fonde con DEFAULT così
# le chiavi mancanti (es. versioni precedenti del file)
# ricevono sempre un valore sensato senza crashare.
# salva() crea la directory se non esiste, poi scrive il JSON
# con indentazione leggibile per permettere modifiche manuali.
# ══════════════════════════════════════════════════════════════

def carica() -> dict:
    """Legge config.json e restituisce un dict completo (con default per le chiavi mancanti)."""
    config = dict(DEFAULT)
    try:
        with open(CONFIG_PATH, "r") as f:
            dati = json.load(f)
        config.update({k: v for k, v in dati.items() if k in DEFAULT})
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return config

def salva(config: dict):
    """Scrive config su disco. Crea la directory se non esiste."""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


# ══════════════════════════════════════════════════════════════
# PARTE 3 — ACCESSO PER CHIAVE
# get() e set() sono shortcut per leggere e scrivere
# una singola impostazione senza gestire il dict completo.
# set() carica, modifica e salva in un'unica operazione,
# così ogni chiamata produce un file JSON sempre consistente.
# ══════════════════════════════════════════════════════════════

def get(chiave: str):
    """Restituisce il valore corrente di una singola impostazione."""
    return carica().get(chiave, DEFAULT.get(chiave))

def set(chiave: str, valore):
    """Aggiorna una singola impostazione e salva su disco."""
    config = carica()
    config[chiave] = valore
    salva(config)
