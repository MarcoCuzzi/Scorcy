#!/usr/bin/env python3
"""
ui_terminal.py — Modalità terminale interattivo di Scorcy (Linux).
Gestisce tutto l'input/output testuale con l'utente.
Importa la logica pura da core.py.
"""

import core


# ══════════════════════════════════════════════════════════════
# PARTE 1 — INTESTAZIONE
# Stampa il banner iniziale con le informazioni di sistema:
# percorso Desktop rilevato (localizzato), cartella icone
# e lista dei browser trovati sulla macchina.
# ══════════════════════════════════════════════════════════════

def _stampa_intestazione():
    print("=" * 50)
    print("  🔗 Crea Scorciatoia Web per Linux")
    print("=" * 50)
    print(f"  Desktop:        {core.DESKTOP_PATH}")
    print(f"  Cartella icone: {core.ICONS_PATH}")
    if core.BROWSER_DISPONIBILI:
        nomi = ", ".join(n for n, _ in core.BROWSER_DISPONIBILI)
        print(f"  Browser trovati: {nomi}")
    else:
        print("  ⚠️  Nessun browser rilevato, verrà usato xdg-open")
    print()


# ══════════════════════════════════════════════════════════════
# PARTE 2 — SELEZIONE BROWSER
# Mostra la lista numerata dei browser disponibili e chiede
# una scelta. Invio senza numero seleziona il predefinito
# (primo browser rilevato). Ritorna il percorso eseguibile
# del browser scelto, o stringa vuota per il predefinito.
# ══════════════════════════════════════════════════════════════

def _chiedi_browser() -> str:
    if not core.BROWSER_DISPONIBILI:
        return ""
    print("\n🌍 Browser disponibili:")
    print("   0. Predefinito (primo rilevato)")
    for i, (nome, _) in enumerate(core.BROWSER_DISPONIBILI, 1):
        print(f"   {i}. {nome}")
    scelta = input("   Scelta (invio per predefinito): ").strip()
    if scelta.isdigit():
        idx = int(scelta)
        if 1 <= idx <= len(core.BROWSER_DISPONIBILI):
            return core.BROWSER_DISPONIBILI[idx - 1][1]
    return ""


# ══════════════════════════════════════════════════════════════
# PARTE 3 — RACCOLTA DATI
# Chiede all'utente nome, URL, icona e browser in sequenza.
# Valida che il nome non sia vuoto e normalizza l'URL
# aggiungendo https:// se mancante.
# Ritorna una tupla (nome, url, icona, browser_exe).
# ══════════════════════════════════════════════════════════════

def _chiedi_dati() -> tuple[str, str, str, str]:
    while True:
        nome = input("📌 Nome scorciatoia (es. YouTube): ").strip()
        if nome:
            break
        print("⚠️  Il nome non può essere vuoto.")

    url = input("🌐 URL (es. https://youtube.com): ").strip()
    url = core.normalizza_url(url)

    print(f"🖼️  Icona da {core.ICONS_PATH}")
    icona = input("   Nome file icona (es. youtube.png) o invio per saltare: ").strip()

    browser_exe = _chiedi_browser()

    return nome, url, icona, browser_exe


# ══════════════════════════════════════════════════════════════
# PARTE 4 — GESTIONE SOVRASCRITTURA
# Intercetta FileExistsError lanciato da core.crea_scorciatoia
# e chiede conferma all'utente prima di procedere.
# _stampa_risultato centralizza la stampa dei campi dell'oggetto
# Scorciatoia, usata sia per creazione che per sovrascrittura.
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
    except FileExistsError:
        nome_file = core.nome_a_filename(nome)
        if _chiedi_sovrascrittura(nome_file):
            s = core.sovrascrivi_scorciatoia(nome, url, icona, browser_exe)
            _stampa_risultato(s, "sovrascritta")
        else:
            print("⏭️  Operazione annullata.")


# ══════════════════════════════════════════════════════════════
# PARTE 5 — LOOP PRINCIPALE
# Funzione pubblica chiamata da scorcy.py.
# Mostra l'intestazione, entra nel loop di creazione e
# al termine stampa il messaggio finale con il suggerimento
# per il lucchetto GNOME.
# ══════════════════════════════════════════════════════════════

def avvia():
    _stampa_intestazione()

    while True:
        nome, url, icona, browser_exe = _chiedi_dati()
        _crea_con_conferma(nome, url, icona, browser_exe)

        altro = input("\n➕ Aggiungere un'altra? (s/n): ").strip().lower()
        if altro != "s":
            break

    print(f"\n🎉 Fatto! Controlla il Desktop: {core.DESKTOP_PATH}")
    print("💡 Per avviare la GUI installa tkinter:  sudo apt install python3-tk")
