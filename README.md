# scorcy

> Crea scorciatoie web sul desktop con un solo comando.

Scorcy è un tool leggero per creare scorciatoie a siti web direttamente sul Desktop, disponibile per **Linux** e **Windows**.

---

## Piattaforme

| Piattaforma | Implementazione | Cartella |
|---|---|---|
| 🐧 Linux (GNOME / XFCE) | Python 3 | [linux/](linux/) |
| 🪟 Windows 10 / 11 | C++ (WinAPI) | [windows/](windows/) |

Consulta il README specifico per la tua piattaforma per istruzioni dettagliate.

---

## Funzionalità principali

- Crea scorciatoie web sul Desktop in pochi secondi
- Tre modalità: **GUI grafica**, **terminale interattivo**, **argomenti inline**
- Supporto **icone personalizzate** dalla cartella `~/Icons`
- Su Windows: **selezione del browser** (Chrome, Firefox, Edge, Brave, Opera, Vivaldi)
- Nessuna dipendenza esterna oltre a Python 3 (Linux) o MinGW (Windows)

---

## Changelog

### v3.0
- Aggiunta versione Windows in C++ con selezione browser
- Supporto icone personalizzate su entrambe le piattaforme
- Rilevamento automatico browser installati (Windows)
- Creazione automatica cartella `Icons` all'avvio

### v2.0
- Linux: tipo `.desktop` cambiato da `Link` ad `Application` per compatibilità Firefox
- Linux: rilevamento automatico percorso Firefox (apt e snap)
- Aggiunta autorizzazione automatica tramite `gio`

### v1.0
- Prima versione con GUI tkinter e modalità terminale (Linux)

---

## Licenza

Distribuito sotto licenza [MIT](LICENSE).
