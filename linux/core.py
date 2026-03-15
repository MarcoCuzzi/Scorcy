#!/usr/bin/env python3
"""
core.py — Logica pura di Scorcy (Linux).
Nessuna dipendenza da UI: niente input(), niente tkinter.
Importato da ui_terminal.py, ui_gui.py e scorcy.py.
"""

import os
import stat
import subprocess
from urllib.parse import urlparse
from typing import NamedTuple

import config as _cfg


# ══════════════════════════════════════════════════════════════
# PARTE 1 — CONFIGURAZIONE
# DESKTOP_PATH viene rilevato tramite xdg-user-dir per
# supportare nomi localizzati (es. "Scrivania" su Debian
# italiano). ICONS_PATH e BROWSER_DEFAULT sono letti dalla
# configurazione persistente tramite config.py, così
# l'utente può cambiarli dal menu impostazioni senza
# modificare il codice.
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

def _icons_path() -> str:
    return _cfg.get("icons_path") or os.path.expanduser("~/Scorcy/Icons")

def _aggiorna_icons_dir():
    os.makedirs(_icons_path(), exist_ok=True)

_aggiorna_icons_dir()

# Proprietà dinamica: riletta dalla config ad ogni accesso
# così le UI rispecchiano sempre il valore salvato.
@property
def ICONS_PATH(self) -> str:  # type: ignore[misc]
    return _icons_path()

# Accesso diretto usato nel resto del modulo
ICONS_PATH = _icons_path()


# ══════════════════════════════════════════════════════════════
# PARTE 2 — RILEVAMENTO BROWSER
# CANDIDATI_BROWSER elenca tutti i browser supportati con i
# loro percorsi alternativi (apt, snap, flatpak, custom).
# rileva_browser() scorre la lista e restituisce solo i browser
# effettivamente installati come lista di tuple (nome, percorso).
# BROWSER_DISPONIBILI è calcolato all'avvio.
# browser_default() legge la preferenza da config e ricade
# sul primo browser disponibile se la preferenza non è più
# valida (es. browser disinstallato).
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


# ══════════════════════════════════════════════════════════════
# PARTE 2b — ICONE BROWSER DI SISTEMA
# cerca_icona_browser() cerca la PNG del browser in
# /usr/share/icons/hicolor/ provando le dimensioni più comuni
# (48x48, 32x32, 128x128, 256x256) e i nomi icona tipici
# di ciascun browser. Restituisce il percorso se trovato,
# None altrimenti. Nessuna dipendenza esterna: solo os.path.
# ══════════════════════════════════════════════════════════════

# Mappa nome browser → nomi icona tipici in hicolor
_ICONA_BROWSER: dict[str, list[str]] = {
    "Firefox":     ["firefox", "firefox-esr", "org.mozilla.firefox"],
    "Chrome":      ["google-chrome", "chrome"],
    "Chromium":    ["chromium", "chromium-browser"],
    "Brave":       ["brave-browser", "com.brave.Browser"],
    "Edge":        ["microsoft-edge", "com.microsoft.Edge"],
    "Opera":       ["opera"],
    "Vivaldi":     ["vivaldi", "vivaldi-stable"],
    "Tor Browser": ["tor-browser", "torbrowser"],
    "Epiphany":    ["epiphany", "org.gnome.Epiphany"],
    "Falkon":      ["falkon", "org.kde.falkon"],
    "Midori":      ["midori", "org.gnome.Midori"],
    "qutebrowser": ["qutebrowser", "org.qutebrowser.qutebrowser"],
}

_HICOLOR_BASE  = "/usr/share/icons/hicolor"
_HICOLOR_SIZES = ["48x48", "32x32", "128x128", "256x256", "64x64"]

def cerca_icona_browser(nome: str) -> str | None:
    """
    Cerca la PNG del browser in /usr/share/icons/hicolor/.
    Restituisce il percorso completo se trovato, None altrimenti.
    """
    for nome_icona in _ICONA_BROWSER.get(nome, []):
        for size in _HICOLOR_SIZES:
            path = os.path.join(_HICOLOR_BASE, size, "apps", nome_icona + ".png")
            if os.path.isfile(path):
                return path
    return None


# ══════════════════════════════════════════════════════════════
# PARTE 2c — ICONA COMPOSITA (richiede Pillow)
# PILLOW_DISPONIBILE indica se Pillow è installato.
# genera_icona_composita() sovrappone la PNG del browser
# come badge in basso a destra sull'icona principale.
# Se Pillow non è disponibile o qualcosa va storto,
# restituisce None silenziosamente — crea_scorciatoia
# usa allora l'icona base senza badge.
# Le icone generate vengono salvate in ~/Scorcy/Icons/generated/
# con nome deterministico basato su icona+browser, così
# la stessa combinazione non viene rigenerata ogni volta.
# ══════════════════════════════════════════════════════════════

try:
    from PIL import Image
    PILLOW_DISPONIBILE = True
except ImportError:
    PILLOW_DISPONIBILE = False

def genera_icona_composita(icon_path: str, browser_exe: str) -> str | None:
    """
    Genera una PNG con l'icona principale e il badge del browser
    sovrapposto in basso a destra. Restituisce il percorso della
    PNG generata, o None se Pillow non è disponibile o in caso
    di errore.
    """
    if not PILLOW_DISPONIBILE:
        return None

    # Cerca icona browser di sistema
    nome_b = nome_browser_da_exe(browser_exe) if browser_exe else ""
    badge_path = cerca_icona_browser(nome_b) if nome_b else None

    # Se non c'è badge non vale la pena generare
    if not badge_path:
        return None

    # Controlla che l'icona base sia un file reale (non un fallback testuale)
    if not os.path.isfile(icon_path):
        return None

    try:
        from PIL import Image

        base  = Image.open(icon_path).convert("RGBA")
        badge = Image.open(badge_path).convert("RGBA")

        # Dimensione base normalizzata a 48x48
        SIZE = 48
        base = base.resize((SIZE, SIZE), Image.LANCZOS)

        # Badge: 1/3 della base
        badge_size = SIZE // 3
        badge = badge.resize((badge_size, badge_size), Image.LANCZOS)

        # Incolla badge in basso a destra
        pos = (SIZE - badge_size, SIZE - badge_size)
        composita = base.copy()
        composita.paste(badge, pos, badge)

        # Percorso output deterministico
        generated_dir = os.path.join(_icons_path(), "generated")
        os.makedirs(generated_dir, exist_ok=True)

        nome_base  = os.path.splitext(os.path.basename(icon_path))[0]
        nome_badge = os.path.splitext(os.path.basename(badge_path))[0]
        out_path   = os.path.join(generated_dir, f"{nome_base}__{nome_badge}.png")

        composita.save(out_path, "PNG")
        return out_path

    except Exception:
        return None


def browser_default() -> str:
    """
    Restituisce il percorso del browser preferito dalla config.
    Se non impostato o non più valido, ricade sul primo disponibile.
    """
    preferito = _cfg.get("browser_default")
    if preferito and any(exe == preferito for _, exe in BROWSER_DISPONIBILI):
        return preferito
    return BROWSER_DISPONIBILI[0][1] if BROWSER_DISPONIBILI else "xdg-open"


# ══════════════════════════════════════════════════════════════
# PARTE 3 — VALIDAZIONE URL
# valida_url() usa urllib.parse per un controllo sintattico
# completo: verifica presenza di schema (http/https),
# netloc non vuoto e almeno un punto nel dominio.
# Restituisce None se l'URL è valido, altrimenti una stringa
# con la descrizione del problema, così le UI possono
# mostrare un messaggio specifico senza conoscere i dettagli.
# La validazione viene eseguita solo se url_validation è
# abilitata nella config; in caso contrario la funzione
# restituisce sempre None (nessun errore).
# ══════════════════════════════════════════════════════════════

def valida_url(url: str) -> str | None:
    """
    Controlla la validità sintattica dell'URL.
    Restituisce None se valido, stringa di errore altrimenti.
    Se url_validation è disabilitata in config, restituisce sempre None.
    """
    if not _cfg.get("url_validation"):
        return None

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return "L'URL deve iniziare con http:// o https://"

    if not parsed.netloc:
        return "L'URL non contiene un dominio valido."

    dominio = parsed.netloc.split(":")[0]  # rimuove la porta se presente

    # Nessuno spazio nel dominio
    if " " in dominio:
        return f"Il dominio contiene spazi: '{dominio}'"

    # Almeno un punto nel dominio
    if "." not in dominio:
        return f"Il dominio '{dominio}' non sembra valido (manca il punto)."

    # Nessun segmento vuoto (doppi punti tipo "a..b.com")
    parti = dominio.split(".")
    if any(p == "" for p in parti):
        return f"Il dominio '{dominio}' contiene punti consecutivi."

    # TLD (ultima parte) deve essere almeno 2 caratteri
    tld = parti[-1]
    if len(tld) < 2:
        return f"Il dominio '{dominio}' non ha un TLD valido."

    return None


# ══════════════════════════════════════════════════════════════
# PARTE 4 — GESTIONE ICONE
# risolvi_icona cerca il file icona in ICONS_PATH corrente
# (riletto dalla config ad ogni chiamata).
# Se il file non ha estensione prova .png, .svg, .jpg, .xpm.
# Il fallback è il nome base del browser scelto (es. "firefox")
# così l'icona del browser viene usata in automatico.
# apri_cartella_icone apre ICONS_PATH nel file manager di
# sistema tramite xdg-open, senza dipendenze UI.
# ══════════════════════════════════════════════════════════════

def risolvi_icona(nome_icona: str, browser_exe: str = "") -> str:
    fallback = os.path.basename(browser_exe).split("-")[0] if browser_exe else "firefox"
    if not nome_icona:
        return fallback
    cartella = _icons_path()
    base = os.path.join(cartella, nome_icona)
    if os.path.isfile(base):
        return base
    for ext in [".png", ".svg", ".jpg", ".xpm"]:
        if os.path.isfile(base + ext):
            return base + ext
    return fallback

def apri_cartella_icone():
    """Apre ICONS_PATH nel file manager. Usata da GUI e sottocomando CLI."""
    try:
        subprocess.Popen(["xdg-open", _icons_path()])
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════
# PARTE 5 — UTILITÀ STRINGHE
# normalizza_url aggiunge https:// se mancante.
# sanitizza_nome rimuove i caratteri non validi per i nomi
# file Linux (carattere null e slash), tronca a 200 caratteri
# e restituisce la stringa pulita. Se il risultato è vuoto
# dopo la pulizia restituisce stringa vuota: chi chiama
# sanitizza_nome deve gestire questo caso mostrando un errore.
# nome_a_filename converte il nome sanitizzato in nome file
# .desktop sostituendo gli spazi con underscore.
# nome_browser_da_exe ricava il nome leggibile dal percorso
# eseguibile cercando in BROWSER_DISPONIBILI.
# ══════════════════════════════════════════════════════════════

def normalizza_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url

def sanitizza_nome(nome: str) -> str:
    """
    Rimuove caratteri non validi per nomi file Linux (null byte e slash),
    tronca a 200 caratteri e fa strip degli spazi.
    Restituisce stringa vuota se il risultato è vuoto.
    """
    pulito = nome.replace("\x00", "").replace("/", "")
    pulito = pulito.strip()[:200]
    return pulito

def nome_a_filename(nome: str) -> str:
    return nome.replace(" ", "_") + ".desktop"

def nome_browser_da_exe(browser_exe: str) -> str:
    return next(
        (n for n, e in BROWSER_DISPONIBILI if e == browser_exe),
        os.path.basename(browser_exe)
    )


# ══════════════════════════════════════════════════════════════
# PARTE 6 — COSTRUZIONE CONTENUTO .desktop
# Genera la stringa del file .desktop secondo lo standard
# freedesktop.org. Separata dalla scrittura su disco per
# poter essere testata in isolamento.
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
# PARTE 7 — SCRITTURA FILE E PERMESSI
# Scrive il file .desktop su disco, imposta i permessi
# eseguibili (rwxr-xr-x) e tenta l'autorizzazione tramite
# il comando gio, necessario su GNOME per evitare il lucchetto.
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
# PARTE 8 — RISULTATO SCORCIATOIA
# NamedTuple restituita da crea_scorciatoia e
# sovrascrivi_scorciatoia. Raccoglie tutti i valori già
# calcolati internamente così le UI non devono ricalcolarli.
# ══════════════════════════════════════════════════════════════

class Scorciatoia(NamedTuple):
    percorso:     str   # percorso completo del file .desktop creato
    url:          str   # URL normalizzato (con https://)
    nome_browser: str   # nome leggibile del browser (es. "Firefox")
    icon_path:    str   # percorso icona o nome fallback (es. "firefox")


# ══════════════════════════════════════════════════════════════
# PARTE 9 — FUNZIONI PRINCIPALI
# crea_scorciatoia orchestra le parti precedenti.
# Lancia ValueError se nome o URL non superano la validazione,
# FileExistsError se il file esiste già.
# sovrascrivi_scorciatoia cancella il file esistente e lo
# ricrea chiamando crea_scorciatoia.
# browser_exe è opzionale: se omesso viene usato browser_default().
# ══════════════════════════════════════════════════════════════

def crea_scorciatoia(nome: str, url: str, icona: str = "",
                     browser_exe: str = "") -> Scorciatoia:
    """
    Crea il file .desktop sul Desktop.
    Lancia ValueError se nome o URL non sono validi.
    Lancia FileExistsError se il file esiste già.
    """
    # Sanitizzazione nome
    nome_pulito = sanitizza_nome(nome)
    if not nome_pulito:
        raise ValueError("Il nome non può essere vuoto o contenere solo caratteri non validi.")

    # Normalizzazione e validazione URL
    url_ok = normalizza_url(url)
    errore_url = valida_url(url_ok)
    if errore_url:
        raise ValueError(errore_url)

    browser      = browser_exe or browser_default()
    nome_browser = nome_browser_da_exe(browser)
    os.makedirs(DESKTOP_PATH, exist_ok=True)

    nome_file     = nome_a_filename(nome_pulito)
    percorso_file = os.path.join(DESKTOP_PATH, nome_file)

    if os.path.exists(percorso_file):
        raise FileExistsError(percorso_file)

    icon_path = risolvi_icona(icona, browser)

    # Tenta icona composita se abilitata in config e Pillow disponibile
    if _cfg.get("composite_icon") and os.path.isfile(icon_path):
        composita = genera_icona_composita(icon_path, browser)
        if composita:
            icon_path = composita

    contenuto = costruisci_contenuto(nome_pulito, url_ok, icon_path, browser, nome_browser)
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
    Lancia ValueError se nome o URL non sono validi.
    """
    nome_pulito   = sanitizza_nome(nome)
    percorso_file = os.path.join(DESKTOP_PATH, nome_a_filename(nome_pulito))
    if os.path.exists(percorso_file):
        os.remove(percorso_file)
    return crea_scorciatoia(nome, url, icona, browser_exe)
