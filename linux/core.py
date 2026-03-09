#!/usr/bin/env python3
"""
core.py — Logica pura di Scorcy (Linux).
Nessuna dipendenza da UI: niente input(), niente tkinter.
Importato da ui_terminal.py, ui_gui.py e scorcy.py.
"""

import os
import stat
import subprocess


# ══════════════════════════════════════════════════════════════
# PARTE 1 — CONFIGURAZIONE
# Costanti globali: percorsi Desktop e cartella icone.
# Usare expanduser garantisce compatibilità con qualsiasi utente,
# eliminando il percorso hardcoded /home/marco presente nella
# versione originale.
# ══════════════════════════════════════════════════════════════

DESKTOP_PATH = os.path.expanduser("~/Desktop")
ICONS_PATH   = os.path.expanduser("~/Icons")


# ══════════════════════════════════════════════════════════════
# PARTE 2 — RILEVAMENTO FIREFOX
# Cerca il percorso eseguibile di Firefox tra le installazioni
# più comuni: pacchetto apt (/usr/bin), snap (/snap/bin),
# o fallback al nome generico se tutto fallisce.
# ══════════════════════════════════════════════════════════════

def trova_firefox() -> str:
    for cmd in ["firefox", "/usr/bin/firefox", "/snap/bin/firefox"]:
        try:
            r = subprocess.run(
                ["which", cmd.split("/")[-1]],
                capture_output=True, text=True
            )
            if r.returncode == 0:
                return r.stdout.strip()
        except Exception:
            pass
    return "firefox"


# ══════════════════════════════════════════════════════════════
# PARTE 3 — GESTIONE ICONE
# Risolve il nome file icona nel percorso assoluto cercando
# dentro ICONS_PATH. Se il file non ha estensione, prova
# automaticamente .png, .svg, .jpg, .xpm in ordine.
# Ritorna "firefox" come fallback silenzioso se non trovata
# (chi chiama decide se mostrare un avviso).
# ══════════════════════════════════════════════════════════════

def risolvi_icona(nome_icona: str) -> str:
    if not nome_icona:
        return "firefox"
    base = os.path.join(ICONS_PATH, nome_icona)
    if os.path.isfile(base):
        return base
    for ext in [".png", ".svg", ".jpg", ".xpm"]:
        if os.path.isfile(base + ext):
            return base + ext
    return "firefox"


# ══════════════════════════════════════════════════════════════
# PARTE 4 — UTILITÀ STRINGHE
# Funzioni pure che normalizzano i dati in ingresso:
# - normalizza_url aggiunge https:// se mancante
# - nome_a_filename converte il nome in nome file .desktop
#   sostituendo gli spazi con underscore
# ══════════════════════════════════════════════════════════════

def normalizza_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url

def nome_a_filename(nome: str) -> str:
    return nome.replace(" ", "_") + ".desktop"


# ══════════════════════════════════════════════════════════════
# PARTE 5 — COSTRUZIONE CONTENUTO .desktop
# Genera la stringa del file .desktop secondo lo standard
# freedesktop.org. Separata dalla scrittura su disco per
# poter essere testata in isolamento.
# ══════════════════════════════════════════════════════════════

def costruisci_contenuto(nome: str, url: str, icon_path: str, firefox: str) -> str:
    return f"""[Desktop Entry]
Version=1.0
Type=Application
Name={nome}
Comment=Apre {nome} in Firefox
Exec={firefox} "{url}"
Icon={icon_path}
Terminal=false
Categories=Network;WebBrowser;
"""


# ══════════════════════════════════════════════════════════════
# PARTE 6 — SCRITTURA FILE E PERMESSI
# Scrive il file .desktop su disco, imposta i permessi
# eseguibili (rwxr-xr-x) e tenta l'autorizzazione tramite
# il comando gio, necessario su GNOME per evitare il lucchetto.
# gio viene ignorato silenziosamente se non disponibile.
# ══════════════════════════════════════════════════════════════

def scrivi_desktop(percorso: str, contenuto: str):
    with open(percorso, "w") as f:
        f.write(contenuto)
    os.chmod(
        percorso,
        stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
        stat.S_IRGRP | stat.S_IXGRP |
        stat.S_IROTH | stat.S_IXOTH
    )
    _autorizza_gio(percorso)

def _autorizza_gio(percorso: str):
    try:
        subprocess.run(
            ["gio", "set", percorso, "metadata::trusted", "true"],
            capture_output=True
        )
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════
# PARTE 7 — FUNZIONE PRINCIPALE
# Punto di ingresso della logica core: orchestra le parti
# precedenti per creare la scorciatoia completa.
# Non interagisce mai con l'utente: se il file esiste già
# lancia FileExistsError, lasciando alla UI la scelta
# su come gestire la sovrascrittura.
# ══════════════════════════════════════════════════════════════

def crea_scorciatoia(nome: str, url: str, icona: str = "", firefox: str = "") -> str:
    """
    Crea il file .desktop sul Desktop.
    Ritorna il percorso del file creato.
    Lancia FileExistsError se il file esiste già.
    """
    firefox = firefox or trova_firefox()
    os.makedirs(DESKTOP_PATH, exist_ok=True)

    nome_file     = nome_a_filename(nome)
    percorso_file = os.path.join(DESKTOP_PATH, nome_file)

    if os.path.exists(percorso_file):
        raise FileExistsError(percorso_file)

    url_ok    = normalizza_url(url)
    icon_path = risolvi_icona(icona)
    contenuto = costruisci_contenuto(nome, url_ok, icon_path, firefox)
    scrivi_desktop(percorso_file, contenuto)

    return percorso_file
