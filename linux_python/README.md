# scorcy — Linux

> Crea scorciatoie web sul desktop Linux con un solo comando.

---

## Indice

- [Panoramica](#panoramica)
- [Compatibilità](#compatibilità)
- [Requisiti](#requisiti)
- [Installazione](#installazione)
- [Utilizzo](#utilizzo)
- [Icone personalizzate](#icone-personalizzate)
- [Struttura del file .desktop generato](#struttura-del-file-desktop-generato)
- [Risoluzione problemi](#risoluzione-problemi)
- [Limitazioni note](#limitazioni-note)
- [Changelog](#changelog)

---

## Panoramica

`scorcy.py` è uno script Python che genera file `.desktop` sul Desktop Linux, permettendo di aprire qualsiasi sito web in Firefox con un doppio clic — esattamente come una scorciatoia di un'applicazione.

Funziona in tre modalità:

| Modalità | Descrizione |
|---|---|
| **GUI** | Finestra grafica con campi di testo (richiede `tkinter`) |
| **Terminale interattivo** | Guida passo passo via prompt |
| **Argomenti inline** | Un solo comando, nessuna interazione |

---

## Compatibilità

Lo script funziona su distribuzioni Linux con desktop environment **GNOME** o **XFCE** e Firefox installato.

| Distribuzione | Stato | Note |
|---|---|---|
| **Ubuntu** 20.04+ | ✅ Supportato | Target principale |
| **Linux Mint** | ✅ Supportato | Ottima compatibilità |
| **Pop!_OS** | ✅ Supportato | Basato su Ubuntu |
| **Zorin OS** | ✅ Supportato | Basato su Ubuntu |
| **Fedora** (GNOME) | ✅ Supportato | Firefox spesso preinstallato |
| **Debian** (GNOME/XFCE) | ✅ Supportato | Piccoli aggiustamenti possibili |
| **Xubuntu / Ubuntu MATE** | ✅ Supportato | XFCE, funziona correttamente |
| **Arch / Manjaro** | ⚠️ Parziale | Richiede installazione manuale delle dipendenze |
| **KDE Plasma** | ⚠️ Parziale | `.desktop` funziona, autorizzazione manuale diversa |
| **openSUSE** | ⚠️ Parziale | `gio` potrebbe non essere disponibile |
| **Server senza GUI** | ❌ Non supportato | Nessun desktop environment |

---

## Requisiti

- Linux con desktop environment **GNOME** o **XFCE**
- Python 3.6+
- Firefox (installato via `apt`, `dnf` o `snap`)
- `tkinter` *(solo per la modalità GUI)*

Verifica la versione di Python:

```bash
python3 --version
```

Installa `tkinter` se necessario:

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

### Metodo 1 — Uso diretto

Scarica il file e avvialo dalla cartella dove si trova:

```bash
cd ~/Scaricati
python3 scorcy.py
```

### Metodo 2 — Comando globale *(consigliato)*

Rende lo script disponibile come comando da qualsiasi percorso:

```bash
sudo cp ~/Scaricati/scorcy.py /usr/local/bin/scorcy
sudo chmod +x /usr/local/bin/scorcy
```

Da questo momento in poi:

```bash
scorcy
```

---

## Utilizzo

### Modalità GUI

```bash
python3 scorcy.py
```

Si apre una finestra con tre campi:

- **Nome** — il testo che apparirà sotto l'icona sul Desktop
- **URL** — indirizzo completo del sito (es. `https://youtube.com`)
- **Icona** — nome del file immagine *(opzionale, vedi sezione [Icone](#icone-personalizzate))*

### Modalità terminale interattivo

```bash
python3 scorcy.py --terminale
```

Lo script guida attraverso i campi uno alla volta e al termine chiede se aggiungere un'altra scorciatoia.

### Modalità argomenti inline

```bash
# Con icona
python3 scorcy.py "YouTube" "https://youtube.com" "youtube.png"

# Senza icona (usa Firefox come default)
python3 scorcy.py "GitHub" "https://github.com"
```

| Argomento | Obbligatorio | Esempio |
|---|---|---|
| `nome` | ✅ | `"YouTube"` |
| `url` | ✅ | `"https://youtube.com"` |
| `icona` | ❌ | `"youtube.png"` |

---

## Icone personalizzate

Lo script legge le icone dalla cartella:

```
~/Icons/
```

Per usare un'icona personalizzata, basta indicare **solo il nome del file** — senza percorso:

```
youtube.png          ✅ corretto
~/Icons/youtube.png  ❌ non necessario
```

**Formati supportati:** `.png`, `.svg`, `.jpg`, `.xpm`

**Rilevamento automatico estensione:** se scrivi `youtube` senza estensione, lo script prova in ordine `.png → .svg → .jpg → .xpm`.

**Fallback:** se il file non viene trovato, viene usata l'icona di Firefox e viene mostrato un avviso.

---

## Struttura del file .desktop generato

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=YouTube
Comment=Apre YouTube in Firefox
Exec=/usr/bin/firefox "https://youtube.com"
Icon=/home/marco/Icons/youtube.png
Terminal=false
Categories=Network;WebBrowser;
```

I file vengono salvati in `~/Desktop/` con nome basato sul campo **Nome**, ad esempio `YouTube.desktop`.

---

## Risoluzione problemi

### L'icona sul Desktop mostra un lucchetto 🔒

GNOME richiede di autorizzare manualmente i file `.desktop` creati da script.

**Soluzione:** clic destro sull'icona → **"Consenti avvio"**

Lo script tenta di autorizzarla automaticamente tramite `gio`, ma su alcune configurazioni è necessario farlo manualmente. Su XFCE questo passaggio non è richiesto.

---

### La scorciatoia non si apre

Verificare che Firefox sia installato e raggiungibile:

```bash
which firefox
firefox --version
```

Se Firefox è installato via **Snap** il percorso potrebbe essere `/snap/bin/firefox`. Lo script lo rileva automaticamente, ma in caso di problemi aprire il file `.desktop` con un editor di testo e verificare la riga `Exec=`.

---

### Il Desktop non esiste

```bash
mkdir ~/Desktop
```

---

### Errore: tkinter non trovato

La modalità GUI richiede `tkinter`. Se non è installato, lo script passa automaticamente alla modalità terminale. Per installarlo vedere la sezione [Requisiti](#requisiti).

---

## Limitazioni note

- Il percorso delle icone è fisso a `~/Icons/`. Per cambiarlo modificare la variabile `ICONS_PATH` all'inizio dello script.
- Lo script apre i link esclusivamente con Firefox. Per usare un altro browser modificare la funzione `trova_firefox()`.
- I nomi delle scorciatoie con caratteri speciali (es. `/`, `\`, `"`) potrebbero causare nomi di file non validi.

---

## Changelog

### v3.0
- Aggiunto supporto icone personalizzate da `~/Icons/`
- Rilevamento automatico estensione icona
- Fallback su icona Firefox se il file non viene trovato

### v2.0
- Cambiato tipo `.desktop` da `Link` ad `Application` per compatibilità con Firefox
- Rilevamento automatico percorso Firefox (apt e snap)
- Aggiunta autorizzazione automatica tramite `gio`

### v1.0
- Prima versione con GUI tkinter e modalità terminale
