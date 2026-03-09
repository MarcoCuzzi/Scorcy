#!/usr/bin/env python3
"""
ui_gui.py — Modalità GUI (tkinter) di Scorcy (Linux).
Costruisce la finestra, gestisce i widget e delega
tutta la logica di creazione a core.py.
"""

import os
import tkinter as tk
from tkinter import messagebox
import core


# ══════════════════════════════════════════════════════════════
# PARTE 1 — TEMA VISIVO
# Dizionario centralizzato con tutti i colori dell'interfaccia.
# Modificare qui per cambiare l'aspetto dell'intera GUI
# senza toccare il codice dei widget.
# ══════════════════════════════════════════════════════════════

THEME = {
    "BG":       "#1e1e2e",
    "CARD":     "#2a2a3e",
    "ACCENT":   "#7c3aed",
    "FG":       "#e2e8f0",
    "MUTED":    "#94a3b8",
    "ENTRY_BG": "#313149",
    "GREEN":    "#4ade80",
}


# ══════════════════════════════════════════════════════════════
# PARTE 2 — WIDGET HELPERS
# Funzioni riutilizzabili per creare i widget standard
# dell'interfaccia con lo stile del tema applicato.
# _make_entry_con_placeholder gestisce il comportamento
# del testo grigio che scompare al focus, salvando il
# placeholder sull'oggetto Entry per poterlo leggere dopo.
# ══════════════════════════════════════════════════════════════

def _make_label(parent, testo: str) -> tk.Label:
    return tk.Label(
        parent, text=testo,
        font=("monospace", 8, "bold"),
        bg=THEME["CARD"], fg=THEME["MUTED"], anchor="w"
    )

def _make_entry_con_placeholder(parent, placeholder: str) -> tk.Entry:
    e = tk.Entry(
        parent,
        font=("monospace", 11),
        bg=THEME["ENTRY_BG"], fg=THEME["MUTED"],
        insertbackground=THEME["FG"],
        relief="flat", bd=6
    )
    e.insert(0, placeholder)
    e._placeholder = placeholder

    def on_focus_in(_):
        if e.get() == e._placeholder:
            e.delete(0, tk.END)
            e.config(fg=THEME["FG"])

    def on_focus_out(_):
        if not e.get():
            e.insert(0, e._placeholder)
            e.config(fg=THEME["MUTED"])

    e.bind("<FocusIn>",  on_focus_in)
    e.bind("<FocusOut>", on_focus_out)
    return e


# ══════════════════════════════════════════════════════════════
# PARTE 3 — LETTURA E RESET ENTRY
# _leggi_entry restituisce il valore reale ignorando il
# placeholder (stringa vuota se l'utente non ha scritto nulla).
# _reset_entry riporta il campo allo stato iniziale con
# il placeholder e il colore muted, usato dopo una creazione
# andata a buon fine.
# ══════════════════════════════════════════════════════════════

def _leggi_entry(e: tk.Entry) -> str:
    v = e.get().strip()
    return "" if v == getattr(e, "_placeholder", None) else v

def _reset_entry(e: tk.Entry):
    e.delete(0, tk.END)
    e.insert(0, e._placeholder)
    e.config(fg=THEME["MUTED"])


# ══════════════════════════════════════════════════════════════
# PARTE 4 — VALIDAZIONE INPUT
# Controlla che nome e URL siano stati compilati prima
# di passare il controllo a core. Ritorna una stringa
# di errore se qualcosa manca, None se tutto è valido.
# Separata dal callback per poter essere testata in isolamento.
# ══════════════════════════════════════════════════════════════

def _valida_input(nome: str, url: str) -> str | None:
    if not nome:
        return "Inserisci il nome della scorciatoia."
    if not url or url == "https://":
        return "Inserisci un URL valido."
    return None


# ══════════════════════════════════════════════════════════════
# PARTE 5 — CALLBACK PULSANTE CREA
# Legge i campi, valida, chiama core.crea_scorciatoia.
# Gestisce FileExistsError chiedendo conferma con una
# finestra di dialogo nativa. In caso di successo aggiorna
# la label di stato e resetta tutti i campi.
# ══════════════════════════════════════════════════════════════

def _on_crea(e_nome, e_url, e_icona, stato_var, root):
    nome  = _leggi_entry(e_nome)
    url   = _leggi_entry(e_url)
    icona = _leggi_entry(e_icona)

    errore = _valida_input(nome, url)
    if errore:
        messagebox.showwarning("Attenzione", errore, parent=root)
        return

    try:
        core.crea_scorciatoia(nome, url, icona)
        stato_var.set(f"✅ '{nome}' creata sul Desktop!")
        for e in (e_nome, e_url, e_icona):
            _reset_entry(e)

    except FileExistsError as e:
        nome_file = core.nome_a_filename(nome)
        if messagebox.askyesno(
            "File esistente",
            f"Esiste già '{nome_file}'.\nSovrascrivere?",
            parent=root
        ):
            os.remove(str(e))
            core.crea_scorciatoia(nome, url, icona)
            stato_var.set(f"✅ '{nome}' sovrascritta sul Desktop!")
            for entry in (e_nome, e_url, e_icona):
                _reset_entry(entry)


# ══════════════════════════════════════════════════════════════
# PARTE 6 — COSTRUZIONE FINESTRA
# Assembla tutti i widget nella finestra principale:
# titolo, frame con i tre campi input, label di stato
# e pulsante di creazione. Ogni widget usa i colori
# del THEME e i helper delle parti precedenti.
# ══════════════════════════════════════════════════════════════

def _costruisci_finestra(root: tk.Tk):
    T = THEME
    root.title("Crea Scorciatoia Web")
    root.geometry("460x390")
    root.resizable(False, False)
    root.configure(bg=T["BG"])

    # Intestazione
    tk.Label(root, text="🔗 Crea Scorciatoia Web",
             font=("monospace", 15, "bold"),
             bg=T["BG"], fg=T["ACCENT"]).pack(pady=(18, 2))
    tk.Label(root, text=f"Firefox: {core.trova_firefox()}",
             font=("monospace", 8),
             bg=T["BG"], fg=T["MUTED"]).pack()

    # Frame campi input
    frame = tk.Frame(root, bg=T["CARD"], padx=24, pady=20)
    frame.pack(padx=20, pady=12, fill="x")

    _make_label(frame, "NOME SCORCIATOIA").pack(fill="x", pady=(8, 2))
    e_nome = _make_entry_con_placeholder(frame, "es. YouTube")
    e_nome.pack(fill="x", ipady=4)

    _make_label(frame, "URL DEL SITO").pack(fill="x", pady=(8, 2))
    e_url = _make_entry_con_placeholder(frame, "https://")
    e_url.pack(fill="x", ipady=4)

    _make_label(frame, f"ICONA — solo nome file da {core.ICONS_PATH}").pack(fill="x", pady=(8, 2))
    e_icona = _make_entry_con_placeholder(frame, "es. youtube.png  (lascia vuoto per default)")
    e_icona.pack(fill="x", ipady=4)

    # Label stato (messaggio di conferma/errore)
    stato_var = tk.StringVar()
    tk.Label(root, textvariable=stato_var,
             font=("monospace", 9),
             bg=T["BG"], fg=T["GREEN"], wraplength=420).pack(pady=4)

    # Pulsante crea
    tk.Button(
        root, text="✚  CREA SCORCIATOIA",
        font=("monospace", 11, "bold"),
        bg=T["ACCENT"], fg="white",
        activebackground="#6d28d9", activeforeground="white",
        relief="flat", bd=0, padx=20, pady=10, cursor="hand2",
        command=lambda: _on_crea(e_nome, e_url, e_icona, stato_var, root)
    ).pack(pady=(0, 16))


# ══════════════════════════════════════════════════════════════
# PARTE 7 — AVVIO GUI
# Funzione pubblica chiamata da scorcy.py.
# Se tkinter non è disponibile cade automaticamente
# sulla modalità terminale senza crash.
# ══════════════════════════════════════════════════════════════

def avvia():
    root = tk.Tk()
    _costruisci_finestra(root)
    root.mainloop()
