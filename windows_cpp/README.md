# scorcy — Windows

> Crea scorciatoie web sul desktop Windows con un solo comando.

---

## Indice

- [Panoramica](#panoramica)
- [Requisiti](#requisiti)
- [Compilazione](#compilazione)
- [Utilizzo](#utilizzo)
- [Selezione browser](#selezione-browser)
- [Icone personalizzate](#icone-personalizzate)
- [Risoluzione problemi](#risoluzione-problemi)
- [Limitazioni note](#limitazioni-note)
- [Changelog](#changelog)

---

## Panoramica

`scorcy_win.cpp` è un programma C++ che crea scorciatoie web sul Desktop di Windows. Le scorciatoie si aprono nel browser predefinito oppure in un browser specifico a scelta.

Funziona in tre modalità:

| Modalità | Descrizione |
|---|---|
| **GUI** | Finestra grafica con campi di testo e selezione browser |
| **Terminale interattivo** | Guida passo passo via prompt |
| **Argomenti inline** | Un solo comando, nessuna interazione |

È disponibile anche una versione Python alternativa (`scorcy_win.py`) che non richiede compilazione ma necessita di Python 3 installato.

---

## Requisiti

- Windows 10 o superiore
- **Per la versione C++:** MinGW-w64 (compilatore g++)
- **Per la versione Python:** Python 3.6+

### Installare MinGW

1. Scarica lo zip da [winlibs.com](https://winlibs.com) — versione **GCC, Win64, UCRT**
2. Estrai e sposta la cartella `mingw64` in `%USERPROFILE%\mingw64`
3. Aggiungi al PATH:

```powershell
[System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";$env:USERPROFILE\mingw64\mingw64\bin", "User")
$env:Path += ";$env:USERPROFILE\mingw64\mingw64\bin"
```

4. Verifica:

```powershell
g++ --version
```

---

## Compilazione

```powershell
g++ scorcy_win.cpp -o scorcy_win.exe -mwindows -municode -lole32 -luuid
```

I flag `-lole32 -luuid` sono necessari per la creazione di file `.lnk` tramite COM.

---

## Utilizzo

### Modalità GUI

```powershell
.\scorcy_win.exe
```

Si apre una finestra con quattro campi:

- **Nome** — il testo che apparirà sotto l'icona sul Desktop
- **URL** — indirizzo completo del sito (es. `https://youtube.com`)
- **Icona** — nome del file immagine *(opzionale)*
- **Browser** — selezione dal menu a discesa *(opzionale)*

### Modalità terminale interattivo

```powershell
.\scorcy_win.exe --terminale
```

### Modalità argomenti inline

```powershell
# Solo nome e URL (browser predefinito)
.\scorcy_win.exe "YouTube" "https://youtube.com"

# Con icona
.\scorcy_win.exe "YouTube" "https://youtube.com" "youtube.ico"

# Con browser specifico
.\scorcy_win.exe "YouTube" "https://youtube.com" "" "chrome"

# Completo
.\scorcy_win.exe "YouTube" "https://youtube.com" "youtube.ico" "firefox"
```

| Argomento | Obbligatorio | Esempio |
|---|---|---|
| `nome` | ✅ | `"YouTube"` |
| `url` | ✅ | `"https://youtube.com"` |
| `icona` | ❌ | `"youtube.ico"` |
| `browser` | ❌ | `"chrome"` / `"firefox"` / `"edge"` |

---

## Selezione browser

All'avvio lo script rileva automaticamente i browser installati cercando nei percorsi standard:

| Browser | Percorso cercato |
|---|---|
| Google Chrome | `Program Files\Google\Chrome\...` |
| Mozilla Firefox | `Program Files\Mozilla Firefox\...` |
| Microsoft Edge | `Program Files\Microsoft\Edge\...` |
| Brave | `Program Files\BraveSoftware\...` |
| Opera | `Program Files\Opera\...` |
| Vivaldi | `Program Files\Vivaldi\...` |

Con **Browser predefinito** viene creato un file `.url` standard Windows. Con un browser specifico viene creato un file `.lnk` (collegamento nativo) che lancia direttamente quel browser con l'URL.

---

## Icone personalizzate

Lo script legge le icone dalla cartella:

```
%USERPROFILE%\Icons\
```

La cartella viene creata automaticamente all'avvio se non esiste. Per usare un'icona personalizzata, indicare **solo il nome del file**:

```
youtube.ico          ✅ corretto
C:\Users\...\Icons\youtube.ico   ❌ non necessario
```

**Formati supportati:** `.ico`, `.png`, `.jpg`, `.bmp`

**Rilevamento automatico estensione:** se scrivi `youtube` senza estensione, lo script prova in ordine `.ico → .png → .jpg → .bmp`.

> ⚠️ **Nota:** Windows memorizza le icone in una cache. Se sostituisci un file icona potrebbe essere necessario disconnettersi e riaccedere per vedere l'aggiornamento.

---

## Risoluzione problemi

### Errore: g++ non riconosciuto

MinGW non è nel PATH. Seguire la sezione [Installare MinGW](#installare-mingw) e verificare con `g++ --version` in una nuova finestra PowerShell.

---

### La scorciatoia non si apre con il browser scelto

Verificare che il browser sia installato nel percorso standard. Browser installati in cartelle personalizzate non vengono rilevati automaticamente.

---

### L'icona non cambia dopo aver sostituito il file

Windows usa una cache delle icone. Per forzare l'aggiornamento:

```powershell
Stop-Process -Name explorer -Force
Remove-Item "$env:LOCALAPPDATA\IconCache.db" -Force
Remove-Item "$env:LOCALAPPDATA\Microsoft\Windows\Explorer\iconcache*" -Force
Start-Process explorer
```

---

## Limitazioni note

- Il percorso delle icone è fisso a `%USERPROFILE%\Icons\`. Per cambiarlo modificare la costante `ICONS_SUBDIR` nel sorgente.
- Il rilevamento browser cerca solo nei percorsi di installazione standard.
- I nomi con caratteri speciali (`\ / : * ? " < > |`) vengono automaticamente rimossi.

---

## Changelog

### v1.1
- Aggiunta selezione browser con rilevamento automatico
- File `.lnk` per browser specifici tramite IShellLink COM
- Creazione automatica cartella `%USERPROFILE%\Icons` all'avvio

### v1.0
- Prima versione Windows con GUI, terminale e modalità inline
- Supporto icone personalizzate
- File `.url` per browser predefinito
