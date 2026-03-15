#!/usr/bin/env python3
"""
ui_terminal.py — Modalità terminale interattivo di Scorcy (Linux).
Gestisce tutto l'input/output testuale con l'utente.
Importa la logica pura da core.py e la configurazione da config.py.
"""

import core
import config as cfg


# ══════════════════════════════════════════════════════════════
# PARTE 1 — INTESTAZIONE
# Stampa il banner iniziale con le informazioni di sistema:
# percorso Desktop rilevato, cartella icone, browser trovati
# e stato attuale della validazione URL dalla config.
# ══════════════════════════════════════════════════════════════

def _stampa_intestazione():
    conf         = cfg.carica()
    val_stato    = "attiva ✅" if conf.get("url_validation") else "disattiva ⏸️"
    default_exe  = conf.get("browser_default", "")
    default_nome = next((n for n, e in core.BROWSER_DISPONIBILI if e == default_exe), "primo rilevato")

    print("=" * 52)
    print("  🔗 Crea Scorciatoia Web per Linux")
    print("=" * 52)
    print(f"  Desktop:          {core.DESKTOP_PATH}")
    print(f"  Cartella icone:   {conf.get('icons_path')}")
    print(f"  Validazione URL:  {val_stato}")
    print(f"  Browser default:  {default_nome}")
    if core.BROWSER_DISPONIBILI:
        nomi = ", ".join(n for n, _ in core.BROWSER_DISPONIBILI)
        print(f"  Browser trovati:  {nomi}")
    else:
        print("  ⚠️  Nessun browser rilevato, verrà usato xdg-open")
    print()


# ══════════════════════════════════════════════════════════════
# PARTE 2 — MENU IMPOSTAZIONI
# Mostra le impostazioni correnti e permette di modificarle
# una alla volta. Le modifiche vengono accumulate in un dict
# locale e salvate solo alla fine con cfg.salva(), così
# il comportamento è coerente con la GUI (salvataggio esplicito).
# ══════════════════════════════════════════════════════════════

def _menu_impostazioni():
    conf = cfg.carica()

    print()
    print("─" * 40)
    print("  ⚙️  Impostazioni")
    print("─" * 40)

    # Mostra valori correnti
    val_stato    = "attiva" if conf.get("url_validation") else "disattiva"
    default_exe  = conf.get("browser_default", "")
    default_nome = next((n for n, e in core.BROWSER_DISPONIBILI if e == default_exe), "primo rilevato")
    icons_path   = conf.get("icons_path", "")

    print(f"  1. Validazione URL:   {val_stato}")
    print(f"  2. Browser default:   {default_nome}")
    print(f"  3. Cartella icone:    {icons_path}")
    print(f"  0. Torna al menu principale senza salvare")
    print()

    nuova_conf = dict(conf)
    modificato = False

    scelta = input("  Quale impostazione vuoi modificare? (0-3): ").strip()

    if scelta == "1":
        attuale = nuova_conf.get("url_validation", True)
        nuovo   = not attuale
        nuova_conf["url_validation"] = nuovo
        stato   = "attivata ✅" if nuovo else "disattivata ⏸️"
        print(f"  Validazione URL {stato}")
        modificato = True

    elif scelta == "2":
        if not core.BROWSER_DISPONIBILI:
            print("  ⚠️  Nessun browser rilevato.")
        else:
            print()
            print("  Browser disponibili:")
            for i, (nome, _) in enumerate(core.BROWSER_DISPONIBILI, 1):
                print(f"    {i}. {nome}")
            s = input("  Scelta (invio per primo disponibile): ").strip()
            if s.isdigit():
                idx = int(s)
                if 1 <= idx <= len(core.BROWSER_DISPONIBILI):
                    nuova_conf["browser_default"] = core.BROWSER_DISPONIBILI[idx - 1][1]
                    print(f"  Browser default: {core.BROWSER_DISPONIBILI[idx - 1][0]}")
                    modificato = True
                else:
                    print("  ⚠️  Scelta non valida, nessuna modifica.")
            else:
                nuova_conf["browser_default"] = ""
                print("  Browser default: primo rilevato")
                modificato = True

    elif scelta == "3":
        import os
        nuovo_path = input(f"  Nuova cartella icone [{icons_path}]: ").strip()
        if nuovo_path:
            nuova_conf["icons_path"] = os.path.expanduser(nuovo_path)
            print(f"  Cartella icone: {nuova_conf['icons_path']}")
            modificato = True
        else:
            print("  Nessuna modifica.")

    elif scelta == "0":
        print("  Nessuna modifica salvata.")
        return

    else:
        print("  ⚠️  Scelta non valida.")
        return

    # Chiedi conferma salvataggio
    if modificato:
        salva = input("\n  Salvare le modifiche? (s/n): ").strip().lower()
        if salva == "s":
            cfg.salva(nuova_conf)
            print("  ✅ Impostazioni salvate.")
        else:
            print("  ⏭️  Modifiche annullate.")


# ══════════════════════════════════════════════════════════════
# PARTE 3 — SELEZIONE BROWSER
# Mostra la lista numerata dei browser disponibili e chiede
# una scelta. Invio senza numero usa il browser default
# dalla configurazione.
# ══════════════════════════════════════════════════════════════

def _chiedi_browser() -> str:
    if not core.BROWSER_DISPONIBILI:
        return ""
    default_exe  = cfg.get("browser_default")
    default_nome = next(
        (n for n, e in core.BROWSER_DISPONIBILI if e == default_exe),
        core.BROWSER_DISPONIBILI[0][0]
    )
    print(f"\n🌍 Browser disponibili (default: {default_nome}):")
    for i, (nome, _) in enumerate(core.BROWSER_DISPONIBILI, 1):
        print(f"   {i}. {nome}")
    scelta = input("   Scelta (invio per default): ").strip()
    if scelta.isdigit():
        idx = int(scelta)
        if 1 <= idx <= len(core.BROWSER_DISPONIBILI):
            return core.BROWSER_DISPONIBILI[idx - 1][1]
    return ""


# ══════════════════════════════════════════════════════════════
# PARTE 4 — RACCOLTA DATI
# Chiede nome, URL, icona e browser in sequenza.
# La sanitizzazione del nome viene mostrata all'utente se
# il nome viene modificato dalla pulizia dei caratteri.
# La validazione URL è condizionale alla config: se attiva,
# il loop continua finché l'URL non è valido.
# ══════════════════════════════════════════════════════════════

def _chiedi_dati() -> tuple[str, str, str, str]:
    # Nome
    while True:
        nome = input("📌 Nome scorciatoia (es. YouTube): ").strip()
        if not nome:
            print("⚠️  Il nome non può essere vuoto.")
            continue
        nome_pulito = core.sanitizza_nome(nome)
        if not nome_pulito:
            print("⚠️  Il nome contiene solo caratteri non validi.")
            continue
        if nome_pulito != nome:
            print(f"ℹ️  Nome normalizzato: '{nome_pulito}'")
        nome = nome_pulito
        break

    # URL
    while True:
        url = input("🌐 URL (es. https://youtube.com): ").strip()
        url = core.normalizza_url(url)
        errore = core.valida_url(url)
        if errore:
            print(f"⚠️  {errore}")
            continua = input("   Vuoi inserire un URL diverso? (s/n): ").strip().lower()
            if continua != "s":
                break   # Lascia passare l'URL non valido se l'utente insiste
        else:
            break

    # Icona
    conf = cfg.carica()
    print(f"🖼️  Icona da {conf.get('icons_path')}")
    icona = input("   Nome file icona (es. youtube.png) o invio per saltare: ").strip()

    browser_exe = _chiedi_browser()

    return nome, url, icona, browser_exe


# ══════════════════════════════════════════════════════════════
# PARTE 5 — GESTIONE SOVRASCRITTURA E STAMPA RISULTATO
# Intercetta FileExistsError e ValueError da core e gestisce
# la sovrascrittura chiedendo conferma all'utente.
# ══════════════════════════════════════════════════════════════

def _chiedi_sovrascrittura(nome_file: str) -> bool:
    r = input(f"⚠️  Esiste già '{nome_file}'. Sovrascrivere? (s/n): ").strip().lower()
    return r == "s"

def _stampa_risultato(s: core.Scorciatoia, azione: str):
    print(f"✅ Scorciatoia {azione}: {s.percorso}")
    print(f"   → URL:     {s.url}")
    print(f"   → Browser: {s.nome_browser}")
    print(f"   → Icona:   {s.icon_path}")

def _crea_con_conferma(nome: str, url: str, icona: str, browser_exe: str):
    try:
        s = core.crea_scorciatoia(nome, url, icona, browser_exe)
        _stampa_risultato(s, "creata")
    except ValueError as exc:
        print(f"⚠️  {exc}")
    except FileExistsError:
        nome_file = core.nome_a_filename(nome)
        if _chiedi_sovrascrittura(nome_file):
            s = core.sovrascrivi_scorciatoia(nome, url, icona, browser_exe)
            _stampa_risultato(s, "sovrascritta")
        else:
            print("⏭️  Operazione annullata.")


# ══════════════════════════════════════════════════════════════
# PARTE 6 — MENU PRINCIPALE E LOOP
# Funzione pubblica chiamata da scorcy.py.
# Mostra un menu iniziale con le azioni disponibili,
# inclusa la voce [s] per le impostazioni.
# ══════════════════════════════════════════════════════════════

def avvia():
    _stampa_intestazione()

    while True:
        print("─" * 40)
        print("  [c] Crea nuova scorciatoia")
        print("  [s] Impostazioni")
        print("  [q] Esci")
        print("─" * 40)
        scelta = input("  Scelta: ").strip().lower()

        if scelta == "c":
            nome, url, icona, browser_exe = _chiedi_dati()
            _crea_con_conferma(nome, url, icona, browser_exe)
            print()

        elif scelta == "s":
            _menu_impostazioni()
            print()

        elif scelta in ("q", ""):
            break

        else:
            print("  ⚠️  Scelta non valida.")
            print()

    print(f"\n🎉 Fatto! Controlla il Desktop: {core.DESKTOP_PATH}")
