#!/usr/bin/env python3
"""
ui_terminal.py — Modalità terminale interattivo di Scorcy (Linux).
Gestisce tutto l'input/output testuale con l'utente.
Importa la logica pura da core.py.
"""

import os
import core


# ══════════════════════════════════════════════════════════════
# PARTE 1 — INTESTAZIONE
# Stampa il banner iniziale con le informazioni di sistema:
# percorso Firefox rilevato e cartella icone configurata.
# ══════════════════════════════════════════════════════════════

def _stampa_intestazione():
    firefox = core.trova_firefox()
    print("=" * 50)
    print("  🔗 Crea Scorciatoia Web per Ubuntu (Firefox)")
    print("=" * 50)
    print(f"  Firefox trovato: {firefox}")
    print(f"  Cartella icone:  {core.ICONS_PATH}")
    print()


# ══════════════════════════════════════════════════════════════
# PARTE 2 — RACCOLTA DATI
# Chiede all'utente nome, URL e icona in sequenza.
# Valida che il nome non sia vuoto e normalizza l'URL
# aggiungendo https:// se mancante.
# Ritorna una tupla (nome, url, icona).
# ══════════════════════════════════════════════════════════════

def _chiedi_dati() -> tuple[str, str, str]:
    while True:
        nome = input("📌 Nome scorciatoia (es. YouTube): ").strip()
        if nome:
            break
        print("⚠️  Il nome non può essere vuoto.")

    url = input("🌐 URL (es. https://youtube.com): ").strip()
    url = core.normalizza_url(url)

    print(f"🖼️  Icona da {core.ICONS_PATH}")
    icona = input("   Nome file icona (es. youtube.png) o invio per saltare: ").strip()

    return nome, url, icona


# ══════════════════════════════════════════════════════════════
# PARTE 3 — GESTIONE SOVRASCRITTURA
# Intercetta FileExistsError lanciato da core.crea_scorciatoia
# e chiede conferma all'utente prima di procedere.
# In caso di conferma, rimuove il file esistente e richiama
# core per ricrearlo pulito.
# ══════════════════════════════════════════════════════════════

def _chiedi_sovrascrittura(nome_file: str) -> bool:
    r = input(f"⚠️  Esiste già '{nome_file}'. Sovrascrivere? (s/n): ").strip().lower()
    return r == "s"

def _crea_con_conferma(nome: str, url: str, icona: str):
    try:
        percorso = core.crea_scorciatoia(nome, url, icona)
        print(f"✅ Scorciatoia creata: {percorso}")
        print(f"   → URL:   {url}")
        print(f"   → Icona: {core.risolvi_icona(icona)}")
    except FileExistsError as e:
        nome_file = core.nome_a_filename(nome)
        if _chiedi_sovrascrittura(nome_file):
            os.remove(str(e))
            percorso = core.crea_scorciatoia(nome, url, icona)
            print(f"✅ Scorciatoia sovrascritta: {percorso}")
        else:
            print("⏭️  Operazione annullata.")


# ══════════════════════════════════════════════════════════════
# PARTE 4 — LOOP PRINCIPALE
# Funzione pubblica chiamata da scorcy.py.
# Mostra l'intestazione, entra nel loop di creazione e
# al termine stampa il messaggio finale con il suggerimento
# per il lucchetto GNOME.
# ══════════════════════════════════════════════════════════════

def avvia():
    _stampa_intestazione()

    while True:
        nome, url, icona = _chiedi_dati()
        _crea_con_conferma(nome, url, icona)

        altro = input("\n➕ Aggiungere un'altra? (s/n): ").strip().lower()
        if altro != "s":
            break

    print(f"\n🎉 Fatto! Controlla il Desktop: {core.DESKTOP_PATH}")
    print("💡 Se vedi un lucchetto → clic destro sull'icona → 'Consenti avvio'")
