#!/usr/bin/env python3
"""
core.py — Logica pura di Scorcy (Linux).
Nessuna dipendenza da UI: niente input(), niente tkinter.
Importato da ui_terminal.py, ui_gui.py e scorcy.py.
"""

import os
import stat
import subprocess
from typing import NamedTuple


# ══════════════════════════════════════════════════════════════
# PARTE 1 — CONFIGURAZIONE
# Costanti globali: percorsi Desktop e cartella icone.
# trova_desktop() usa xdg-user-dir per supportare nomi
# localizzati (es. "Scrivania" su Debian italiano).
# ICONS_PATH viene creata automaticamente se non esiste,
# così l'utente trova sempre la cartella pronta all'uso.
# ══════════════════════════════════════════════════════════════

def trova_desktop() -> str:
    try:
        r = subprocess.run(
            ["xdg-user-dir", "DESKTOP"],
            capture_output=True, text=True
        )
        if r.returncode == 0:
            path = r.stdout.strip()
            if path and path != os.path.expanduser("~"):
                return path
    except Exception:
        pass
    return os.path.expanduser("~/Desktop")

DESKTOP_PATH = trova_desktop()
ICONS_PATH   = os.path.expanduser("~/Scorcy/Icons")

os.makedirs(ICONS_PATH, exist_ok=True)


# ══════════════════════════════════════════════════════════════
# PARTE 2 — RILEVAMENTO BROWSER
# CANDIDATI_BROWSER elenca tutti i browser supportati con i
# loro percorsi alternativi (apt, snap, flatpak, custom).
# rileva_browser() scorre la lista e restituisce solo i browser
# effettivamente installati come lista di tuple (nome, percorso).
# BROWSER_DISPONIBILI e BROWSER_DEFAULT sono calcolati
# all'avvio e usati da tutta l'applicazione.
# ══════════════════════════════════════════════════════════════

CANDIDATI_BROWSER = [
    ("Firefox",     ["firefox", "/usr/bin/firefox", "/snap/bin/firefox"]),
    ("Chrome",      ["google-chrome", "google-chrome-stable", "/usr/bin/google-chrome"]),
    ("Chromium",    ["chromium", "chromium-browser", "/usr/bin/chromium", "/usr/bin/chromium-browser"]),
    ("Brave",       ["brave-browser", "/usr/bin/brave-browser", "/opt/brave.com/brave/brave-browser"]),
    ("Edge",        ["microsoft-edge", "microsoft-edge-stable", "/usr/bin/microsoft-edge"]),
    ("Opera",       ["opera", "/usr/bin/opera"]),
    ("Vivaldi",     ["vivaldi", "/usr/bin/vivaldi"]),
    ("Tor Browser", ["torbrowser-launcher", "/usr/bin/torbrowser-launcher"]),
    ("Epiphany",    ["epiphany", "epiphany-browser", "/usr/bin/epiphany"]),
    ("Falkon",      ["falkon", "/usr/bin/falkon"]),
    ("Midori",      ["midori", "/usr/bin/midori"]),
    ("qutebrowser", ["qutebrowser", "/usr/bin/qutebrowser"]),
]

def rileva_browser() -> list[tuple[str, str]]:
    """Restituisce lista di (nome, percorso) per i browser installati."""
    trovati = []
    for nome, comandi in CANDIDATI_BROWSER:
        for cmd in comandi:
            try:
                if cmd.startswith("/"):
                    exe = cmd
                else:
                    r = subprocess.run(["which", cmd], capture_output=True, text=True)
                    exe = r.stdout.strip() if r.returncode == 0 else None
                if exe and os.path.isfile(exe):
                    trovati.append((nome, exe))
                    break
            except Exception:
                pass
    return trovati

BROWSER_DISPONIBILI: list[tuple[str, str]] = rileva_browser()
BROWSER_DEFAULT: str = BROWSER_DISPONIBILI[0][1] if BROWSER_DISPONIBILI else "xdg-open"


# ══════════════════════════════════════════════════════════════
# PARTE 3 — GESTIONE ICONE
# risolvi_icona cerca il file icona in ICONS_PATH.
# Se il file non ha estensione prova .png, .svg, .jpg, .xpm.
# Il fallback è il nome base del browser scelto (es. "firefox",
# "brave") così l'icona del browser viene usata in automatico.
# apri_cartella_icone apre ICONS_PATH nel file manager di
# sistema tramite xdg-open, senza dipendenze UI.
# ══════════════════════════════════════════════════════════════

def risolvi_icona(nome_icona: str, browser_exe: str = "") -> str:
    fallback = os.path.basename(browser_exe).split("-")[0] if browser_exe else "firefox"
    if not nome_icona:
        return fallback
    base = os.path.join(ICONS_PATH, nome_icona)
    if os.path.isfile(base):
        return base
    for ext in [".png", ".svg", ".jpg", ".xpm"]:
        if os.path.isfile(base + ext):
            return base + ext
    return fallback

def apri_cartella_icone():
    """Apre ICONS_PATH nel file manager. Usata da GUI e sottocomando CLI."""
    try:
        subprocess.Popen(["xdg-open", ICONS_PATH])
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════
# PARTE 4 — UTILITÀ STRINGHE
# Funzioni pure che normalizzano i dati in ingresso:
# - normalizza_url aggiunge https:// se mancante
# - nome_a_filename converte il nome in nome file .desktop
#   sostituendo gli spazi con underscore
# - nome_browser_da_exe ricava il nome leggibile dal percorso
#   eseguibile cercando in BROWSER_DISPONIBILI, con fallback
#   al basename del percorso
# ══════════════════════════════════════════════════════════════

def normalizza_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url

def nome_a_filename(nome: str) -> str:
    return nome.replace(" ", "_") + ".desktop"

def nome_browser_da_exe(browser_exe: str) -> str:
    return next(
        (n for n, e in BROWSER_DISPONIBILI if e == browser_exe),
        os.path.basename(browser_exe)
    )


# ══════════════════════════════════════════════════════════════
# PARTE 5 — COSTRUZIONE CONTENUTO .desktop
# Genera la stringa del file .desktop secondo lo standard
# freedesktop.org. Separata dalla scrittura su disco per
# poter essere testata in isolamento.
# Il campo Comment e Exec riflettono il browser scelto.
# ══════════════════════════════════════════════════════════════

def costruisci_contenuto(nome: str, url: str, icon_path: str,
                         browser_exe: str, nome_browser: str) -> str:
    return f"""[Desktop Entry]
Version=1.0
Type=Application
Name={nome}
Comment=Apre {nome} con {nome_browser}
Exec={browser_exe} "{url}"
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
# PARTE 7 — RISULTATO SCORCIATOIA
# Namedtuple restituita da crea_scorciatoia e
# sovrascrivi_scorciatoia. Raccoglie tutti i valori già
# calcolati internamente (percorso, url normalizzato,
# nome browser, percorso icona) così le UI non devono
# ricalcolarli una seconda volta dopo la creazione.
# ══════════════════════════════════════════════════════════════

class Scorciatoia(NamedTuple):
    percorso:     str   # percorso completo del file .desktop creato
    url:          str   # URL normalizzato (con https://)
    nome_browser: str   # nome leggibile del browser (es. "Firefox")
    icon_path:    str   # percorso icona o nome fallback (es. "firefox")


# ══════════════════════════════════════════════════════════════
# PARTE 8 — FUNZIONI PRINCIPALI
# crea_scorciatoia orchestra le parti precedenti per creare
# il file .desktop completo. Non interagisce mai con l'utente:
# se il file esiste già lancia FileExistsError, lasciando alla
# UI la scelta su come gestire la sovrascrittura.
# sovrascrivi_scorciatoia cancella il file esistente e lo
# ricrea chiamando crea_scorciatoia. Tutta la gestione del
# filesystem rimane in core, senza che le UI tocchino os.remove.
# Entrambe restituiscono un oggetto Scorciatoia con tutti i
# valori già pronti, eliminando ricalcoli nelle UI.
# browser_exe è opzionale in entrambe: se omesso viene usato
# BROWSER_DEFAULT.
# ══════════════════════════════════════════════════════════════

def crea_scorciatoia(nome: str, url: str, icona: str = "",
                     browser_exe: str = "") -> Scorciatoia:
    """
    Crea il file .desktop sul Desktop.
    Ritorna un oggetto Scorciatoia con percorso, url, browser e icona.
    Lancia FileExistsError se il file esiste già.
    """
    browser      = browser_exe or BROWSER_DEFAULT
    nome_browser = nome_browser_da_exe(browser)
    os.makedirs(DESKTOP_PATH, exist_ok=True)

    nome_file     = nome_a_filename(nome)
    percorso_file = os.path.join(DESKTOP_PATH, nome_file)

    if os.path.exists(percorso_file):
        raise FileExistsError(percorso_file)

    url_ok    = normalizza_url(url)
    icon_path = risolvi_icona(icona, browser)
    contenuto = costruisci_contenuto(nome, url_ok, icon_path, browser, nome_browser)
    scrivi_desktop(percorso_file, contenuto)

    return Scorciatoia(
        percorso     = percorso_file,
        url          = url_ok,
        nome_browser = nome_browser,
        icon_path    = icon_path,
    )

def sovrascrivi_scorciatoia(nome: str, url: str, icona: str = "",
                             browser_exe: str = "") -> Scorciatoia:
    """
    Cancella il file .desktop esistente e lo ricrea.
    Usata da UI e modalità inline dopo conferma dell'utente.
    Ritorna un oggetto Scorciatoia con percorso, url, browser e icona.
    """
    percorso_file = os.path.join(DESKTOP_PATH, nome_a_filename(nome))
    if os.path.exists(percorso_file):
        os.remove(percorso_file)
    return crea_scorciatoia(nome, url, icona, browser_exe)
