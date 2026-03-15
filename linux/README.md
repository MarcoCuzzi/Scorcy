# Scorcy — Linux

> Crea scorciatoie web sul desktop Linux con un solo comando.

---

## Indice

- [Panoramica](#panoramica)
- [Requisiti](#requisiti)
- [Installazione](#installazione)
- [Utilizzo](#utilizzo)
- [Browser supportati](#browser-supportati)
- [Icone personalizzate](#icone-personalizzate)
- [Struttura del progetto](#struttura-del-progetto)
- [Struttura del file .desktop generato](#struttura-del-file-desktop-generato)
- [Compatibilità](#compatibilità)

---

## Panoramica

Scorcy genera file `.desktop` sul Desktop Linux, permettendo di aprire qualsiasi sito web nel browser scelto con un doppio clic — esattamente come una scorciatoia di un'applicazione nativa.

Funziona in tre modalità:

| Modalità | Descrizione |
|---|---|
| **GUI** | Finestra grafica con tema scuro (richiede `tkinter`) |
| **Terminale interattivo** | Guida passo passo via prompt |
| **Inline** | Un solo comando, nessuna interazione |

---

## Requisiti

- Linux con desktop environment **GNOME** o **XFCE**
- **Python 3.10+**
- Almeno un browser installato
- `tkinter` *(solo per la modalità GUI)*

Verifica la versione di Python:

```bash
python3 --version
```

Installa `tkinter` per la GUI:

```bash
# Ubuntu / Debian / Mint
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch / Manjaro
sudo pacman -S tk
```

---

## Installazione

Clona il repository e spostati nella cartella Linux:

```bash
git clone https://github.com/MarcoCuzzi/scorcy.git
cd scorcy/linux_python
```

### Uso diretto

```bash
python3 scorcy.py
```

### Comando globale *(consigliato)*

Rende `scorcy` disponibile da qualsiasi percorso:

```bash
sudo cp scorcy.py /usr/local/bin/scorcy
sudo chmod +x /usr/local/bin/scorcy
```

Da questo momento:

```bash
scorcy
```

---

## Utilizzo

### GUI

```bash
python3 scorcy.py
```

Apre la finestra grafica. Se `tkinter` non è installato, parte automaticamente la modalità terminale con un promemoria per installarlo.

### Terminale interattivo

```bash
python3 scorcy.py --terminal
# oppure
python3 scorcy.py -t
```

### Inline — creazione diretta da riga di comando

```bash
# Solo nome e URL
python3 scorcy.py "YouTube" "https://youtube.com"

# Con icona personalizzata
python3 scorcy.py "YouTube" "https://youtube.com" "youtube.png"

# Con browser specifico
python3 scorcy.py "YouTube" "https://youtube.com" "youtube.png" "brave"

# Sovrascrive senza chiedere conferma
python3 scorcy.py -f "YouTube" "https://youtube.com"
```

| Argomento | Obbligatorio | Esempio |
|---|---|---|
| `nome` | ✅ | `"YouTube"` |
| `url` | ✅ | `"https://youtube.com"` |
| `icona` | ❌ | `"youtube.png"` |
| `browser` | ❌ | `"firefox"` / `"brave"` / `"chrome"` |

Il flag `-f` può stare in qualsiasi posizione nella riga di comando.

### Altri comandi

```bash
# Apre la cartella icone nel file manager
python3 scorcy.py -icons
python3 scorcy.py -i

# Mostra l'help con i browser rilevati sulla macchina
python3 scorcy.py --help
python3 scorcy.py -h
```

---

## Browser supportati

Scorcy rileva automaticamente all'avvio i browser installati cercando nei percorsi standard. I browser supportati sono:

| Browser | Percorsi cercati |
|---|---|
| Firefox | `apt`, `snap` |
| Chrome | `apt`, percorso standard |
| Chromium | `apt`, percorso standard |
| Brave | `apt`, `/opt/brave.com/` |
| Edge | `apt`, percorso standard |
| Opera | `apt`, percorso standard |
| Vivaldi | `apt`, percorso standard |
| Tor Browser | `torbrowser-launcher` |
| Epiphany | `apt`, percorso standard |
| Falkon | `apt`, percorso standard |
| Midori | `apt`, percorso standard |
| qutebrowser | `apt`, percorso standard |

Se nessun browser viene trovato, viene usato `xdg-open` come fallback (apre l'URL nel browser predefinito di sistema).

---

## Icone personalizzate

Le icone vengono lette dalla cartella:

```
~/Scorcy/Icons/
```

La cartella viene creata automaticamente all'avvio se non esiste. Per usare un'icona personalizzata, copia il file lì dentro e indica solo il nome — senza percorso:

```
youtube.png       ✅ corretto
~/Scorcy/Icons/youtube.png   ❌ non necessario
```

**Formati supportati:** `.png`, `.svg`, `.jpg`, `.xpm`

**Rilevamento automatico estensione:** se scrivi `youtube` senza estensione, Scorcy prova in ordine `.png → .svg → .jpg → .xpm`.

**Fallback:** se il file non viene trovato, viene usata l'icona del browser scelto.

Dalla GUI puoi aprire la cartella icone direttamente con il pulsante 📂 accanto al campo icona, oppure da riga di comando con:

```bash
python3 scorcy.py -i
```

---

## Struttura del progetto

```
linux_python/
├── scorcy.py       ← entry point e routing
├── core.py         ← logica pura (nessuna UI)
├── ui_gui.py       ← interfaccia grafica tkinter
└── ui_terminal.py  ← interfaccia terminale interattivo
```

Tutti e quattro i file devono stare nella stessa cartella.

---

## Struttura del file .desktop generato

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=YouTube
Comment=Apre YouTube con Firefox
Exec=/usr/bin/firefox "https://youtube.com"
Icon=/home/utente/Scorcy/Icons/youtube.png
Terminal=false
Categories=Network;WebBrowser;
```

I file vengono salvati in `~/Desktop/` (o nella cartella Desktop localizzata, rilevata automaticamente tramite `xdg-user-dir`). Il nome del file è basato sul campo **Nome**, ad esempio `YouTube.desktop`.

---

## Compatibilità

| Distribuzione | Stato | Note |
|---|---|---|
| **Ubuntu** 20.04+ | ✅ Supportato | Target principale |
| **Linux Mint** | ✅ Supportato | Ottima compatibilità |
| **Pop!_OS** | ✅ Supportato | Basato su Ubuntu |
| **Zorin OS** | ✅ Supportato | Basato su Ubuntu |
| **Fedora** (GNOME) | ✅ Supportato | |
| **Debian** (GNOME/XFCE) | ✅ Supportato | |
| **Xubuntu / Ubuntu MATE** | ✅ Supportato | |
| **Arch / Manjaro** | ⚠️ Parziale | Dipendenze da installare manualmente |
| **KDE Plasma** | ⚠️ Parziale | `.desktop` funziona, autorizzazione manuale diversa |
| **Server senza GUI** | ❌ Non supportato | Nessun desktop environment |
