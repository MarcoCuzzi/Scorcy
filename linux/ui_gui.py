#!/usr/bin/env python3
"""
ui_gui.py — Modalità GUI (tkinter) di Scorcy (Linux).
Costruisce la finestra, gestisce i widget e delega
tutta la logica di creazione a core.py.
"""

import tkinter as tk
from tkinter import messagebox
import core


# ══════════════════════════════════════════════════════════════
# PARTE 1 — TEMA VISIVO
# Dizionario centralizzato con tutti i colori dell'interfaccia.
# Modificare qui per cambiare l'aspetto dell'intera GUI
# senza toccare il codice dei widget.
# YELLOW è il colore del pulsante "apri cartella icone".
# SCROLL_TRACK e SCROLL_THUMB sono i colori della scrollbar
# custom: traccia scura, pollice viola per coerenza con ACCENT.
# ══════════════════════════════════════════════════════════════

THEME = {
    "BG":           "#1e1e2e",
    "CARD":         "#2a2a3e",
    "ACCENT":       "#7c3aed",
    "FG":           "#e2e8f0",
    "MUTED":        "#94a3b8",
    "ENTRY_BG":     "#313149",
    "GREEN":        "#4ade80",
    "YELLOW":       "#f5a623",
    "SCROLL_TRACK": "#2a2a3e",
    "SCROLL_THUMB": "#5b2db0",
}

BROWSER_EMOJI = {
    "Firefox":     "🦊",
    "Chrome":      "🌐",
    "Chromium":    "🌐",
    "Brave":       "🦁",
    "Edge":        "🌊",
    "Opera":       "🔴",
    "Vivaldi":     "🎵",
    "Tor Browser": "🧅",
    "Epiphany":    "🌍",
    "Falkon":      "🦅",
    "Midori":      "🍃",
    "qutebrowser": "⌨️",
}

def _emoji_browser(nome: str) -> str:
    return BROWSER_EMOJI.get(nome, "🌐")


# ══════════════════════════════════════════════════════════════
# PARTE 2 — SCROLLBAR CUSTOM
# Sostituisce tk.Scrollbar con un Canvas disegnato a mano,
# così traccia e pollice seguono il tema scuro.
# Si collega a un Canvas principale tramite set() e get(),
# che è la stessa interfaccia usata da tk.Scrollbar.
# Il pollice è trascinabile con il mouse; un hover lo schiarisce
# leggermente per feedback visivo. Traccia e pollice sono entrambi
# disegnati come rettangoli con angoli completamente arrotondati.
# La larghezza è 16px con padding interno per un aspetto morbido.
# ══════════════════════════════════════════════════════════════

class _ScrollbarCustom(tk.Canvas):
    LARGHEZZA    = 16
    RAGGIO_THUMB = 8    # raggio pollice — completamente tondo sui lati
    RAGGIO_TRACK = 8    # raggio traccia — stessa forma del pollice
    PADDING      = 3    # spazio tra bordo canvas e traccia/pollice
    THUMB_HOVER  = "#7c3aed"   # ACCENT al hover

    def __init__(self, parent, canvas_target: tk.Canvas, **kwargs):
        super().__init__(
            parent,
            width=self.LARGHEZZA,
            bg=THEME["BG"],          # sfondo = sfondo finestra, la traccia è disegnata
            highlightthickness=0,
            **kwargs
        )
        self._canvas  = canvas_target
        self._thumb   = None
        self._drag_y  = None

        # Collega il canvas target a questa scrollbar
        self._canvas.configure(yscrollcommand=self._aggiorna)

        self.bind("<Configure>",        self._ridisegna)
        self.bind("<ButtonPress-1>",    self._on_click)
        self.bind("<B1-Motion>",        self._on_drag)
        self.bind("<ButtonRelease-1>",  self._on_release)
        self.bind("<Enter>",            self._on_enter)
        self.bind("<Leave>",            self._on_leave)

    # ── Interfaccia verso Canvas target ──────────────────────

    def _aggiorna(self, primo: str, secondo: str):
        """Chiamata dal canvas target quando lo scroll cambia."""
        self._top    = float(primo)
        self._bottom = float(secondo)
        self._ridisegna()

    def _rrect(self, x0, y0, x1, y1, r, colore):
        """Disegna un rettangolo con angoli arrotondati."""
        self.create_arc(x0, y0, x0 + r*2, y0 + r*2, start=90,  extent=90,  fill=colore, outline="")
        self.create_arc(x1 - r*2, y0, x1, y0 + r*2, start=0,   extent=90,  fill=colore, outline="")
        self.create_arc(x0, y1 - r*2, x0 + r*2, y1, start=180, extent=90,  fill=colore, outline="")
        self.create_arc(x1 - r*2, y1 - r*2, x1, y1, start=270, extent=90,  fill=colore, outline="")
        self.create_rectangle(x0 + r, y0,     x1 - r, y1,     fill=colore, outline="")
        self.create_rectangle(x0,     y0 + r, x1,     y1 - r, fill=colore, outline="")

    def _ridisegna(self, _=None):
        self.delete("all")
        h = self.winfo_height()
        w = self.winfo_width()
        if h < 2:
            return

        p = self.PADDING

        # Disegna sempre la traccia arrotondata
        self._rrect(p, p, w - p, h - p, self.RAGGIO_TRACK, THEME["SCROLL_TRACK"])

        top    = getattr(self, "_top",    0.0)
        bottom = getattr(self, "_bottom", 1.0)

        # Non disegnare il pollice se il contenuto entra tutto
        if top <= 0.0 and bottom >= 1.0:
            return

        track_h = h - p * 2
        y0 = p + top    * track_h + p
        y1 = p + bottom * track_h - p
        y1 = max(y1, y0 + self.RAGGIO_THUMB * 2)

        colore = getattr(self, "_colore_thumb", THEME["SCROLL_THUMB"])
        self._rrect(p + 1, y0, w - p - 1, y1, self.RAGGIO_THUMB, colore)

    # ── Interazione mouse ─────────────────────────────────────

    def _on_click(self, event):
        self._drag_y = event.y

    def _on_drag(self, event):
        if self._drag_y is None:
            return
        h     = self.winfo_height()
        delta = (event.y - self._drag_y) / h
        self._drag_y = event.y
        self._canvas.yview_moveto(getattr(self, "_top", 0.0) + delta)

    def _on_release(self, event):
        self._drag_y = None

    def _on_enter(self, _):
        self._colore_thumb = self.THUMB_HOVER
        self._ridisegna()

    def _on_leave(self, _):
        self._colore_thumb = THEME["SCROLL_THUMB"]
        self._ridisegna()


# ══════════════════════════════════════════════════════════════
# PARTE 3 — WIDGET HELPERS
# Funzioni riutilizzabili per creare i widget standard
# dell'interfaccia con lo stile del tema applicato.
# _make_entry_con_placeholder gestisce il comportamento
# del testo grigio che scompare al focus, salvando il
# placeholder sull'oggetto Entry per poterlo leggere dopo.
# _make_btn_cartella crea il pulsante giallo 📂 / "apri"
# accanto al campo icona; usa un Frame con due Label perché
# tkinter Button non supporta layout verticale nativo.
# ══════════════════════════════════════════════════════════════

def _make_label(parent, testo: str) -> tk.Label:
    return tk.Label(
        parent, text=testo,
        font=("monospace", 11, "bold"),
        bg=THEME["CARD"], fg=THEME["FG"], anchor="w"
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

def _make_btn_cartella(parent) -> tk.Frame:
    """Pulsante giallo 📂 / apri che apre ICONS_PATH nel file manager."""
    btn = tk.Frame(parent, bg=THEME["YELLOW"], cursor="hand2")
    tk.Label(btn, text="📂", font=("monospace", 11),
             bg=THEME["YELLOW"], fg="#1e1e2e").pack(padx=6, pady=(3, 0))
    tk.Label(btn, text="apri", font=("monospace", 7, "bold"),
             bg=THEME["YELLOW"], fg="#1e1e2e").pack(padx=6, pady=(0, 3))
    callback = lambda _: core.apri_cartella_icone()
    btn.bind("<Button-1>", callback)
    for child in btn.winfo_children():
        child.bind("<Button-1>", callback)
    return btn

def _make_option_menu(parent, var: tk.StringVar, opzioni: list[str]) -> tk.OptionMenu:
    """OptionMenu stilizzato per la selezione del browser, con emoji."""
    T = THEME
    opzioni_con_emoji = [f"{_emoji_browser(n)}  {n}" for n in opzioni]
    var.set(opzioni_con_emoji[0])

    row = tk.Frame(parent, bg=T["ENTRY_BG"])
    tk.Label(row, text="🌐", font=("monospace", 13),
             bg=T["ENTRY_BG"], fg=T["FG"]).pack(side="right", padx=(0, 8))
    om = tk.OptionMenu(row, var, *opzioni_con_emoji)
    om.config(font=("monospace", 11), bg=T["ENTRY_BG"], fg=T["FG"],
              activebackground="#44445a", activeforeground=T["FG"],
              highlightthickness=0, relief="flat", bd=0, anchor="w",
              indicatoron=0)
    om["menu"].config(font=("monospace", 11), bg=T["ENTRY_BG"], fg=T["FG"],
                      activebackground=T["ACCENT"], activeforeground="white")
    om.pack(side="left", fill="x", expand=True)
    return row


# ══════════════════════════════════════════════════════════════
# PARTE 4 — LETTURA E RESET ENTRY
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
# PARTE 5 — VALIDAZIONE INPUT
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
# PARTE 6 — CALLBACK PULSANTE CREA
# Legge i campi, ricava il browser selezionato dall'OptionMenu,
# valida, chiama core.crea_scorciatoia.
# Gestisce FileExistsError chiedendo conferma con una
# finestra di dialogo nativa. In caso di successo aggiorna
# la label di stato e resetta tutti i campi.
# ══════════════════════════════════════════════════════════════

def _on_crea(e_nome, e_url, e_icona, browser_var, stato_var, root):
    nome        = _leggi_entry(e_nome)
    url         = _leggi_entry(e_url)
    icona       = _leggi_entry(e_icona)
    # Rimuove l'emoji dal nome selezionato per cercare in BROWSER_DISPONIBILI
    nome_b_sel  = browser_var.get().split("  ", 1)[-1]
    browser_exe = next(
        (exe for n, exe in core.BROWSER_DISPONIBILI if n == nome_b_sel), ""
    )

    errore = _valida_input(nome, url)
    if errore:
        messagebox.showwarning("Attenzione", errore, parent=root)
        return

    def _esegui(sovrascrittura=False):
        if sovrascrittura:
            s = core.sovrascrivi_scorciatoia(nome, url, icona, browser_exe)
        else:
            s = core.crea_scorciatoia(nome, url, icona, browser_exe)
        azione = "sovrascritta" if sovrascrittura else "creata"
        stato_var.set(f"✅ '{nome}' {azione} con {s.nome_browser} sul Desktop!")
        for e in (e_nome, e_url, e_icona):
            _reset_entry(e)

    try:
        _esegui()
    except FileExistsError:
        nome_file = core.nome_a_filename(nome)
        if messagebox.askyesno(
            "File esistente",
            f"Esiste già '{nome_file}'.\nSovrascrivere?",
            parent=root
        ):
            _esegui(sovrascrittura=True)


# ══════════════════════════════════════════════════════════════
# PARTE 7 — COSTRUZIONE FINESTRA
# Assembla tutti i widget nella finestra principale.
# Il contenuto è inserito in un Canvas con scrollbar custom
# (_ScrollbarCustom) a colori scuri al posto di tk.Scrollbar.
# Al primo render, _adatta_altezza misura l'altezza reale del
# contenuto e imposta la finestra esattamente a quella misura,
# cappata all'altezza dello schermo disponibile. In questo modo
# la finestra parte sempre abbastanza grande da mostrare tutto
# senza scroll; lo scroll appare solo se l'utente rimpicciolisce
# la finestra o se lo schermo è più piccolo del contenuto.
# La larghezza del frame interno si aggiorna al resize del canvas.
# ══════════════════════════════════════════════════════════════

def _costruisci_finestra(root: tk.Tk):
    T = THEME
    root.title("Scorcy")
    root.resizable(True, True)
    root.minsize(400, 300)
    root.configure(bg=T["BG"])

    # Canvas principale
    canvas = tk.Canvas(root, bg=T["BG"], highlightthickness=0)

    # Scrollbar custom — si collega al canvas internamente
    scrollbar = _ScrollbarCustom(root, canvas_target=canvas)

    # Collega il canvas alla scrollbar per lo scroll da tastiera/rotella
    canvas.configure(yscrollcommand=scrollbar._aggiorna)

    scrollbar.pack(side="right", fill="y", padx=(2, 4), pady=8)
    canvas.pack(side="left", fill="both", expand=True)

    # Frame interno scrollabile
    inner = tk.Frame(canvas, bg=T["BG"])
    inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")

    def _on_frame_configure(_):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _on_canvas_configure(event):
        canvas.itemconfig(inner_id, width=event.width)

    inner.bind("<Configure>", _on_frame_configure)
    canvas.bind("<Configure>", _on_canvas_configure)

    # Scroll con rotella del mouse
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

    def _adatta_altezza(_=None):
        # Aspetta che tutti i widget siano renderizzati, poi misura
        # l'altezza reale del contenuto e adatta la finestra.
        # Se il contenuto supera lo schermo disponibile, la finestra
        # viene cappata e lo scroll diventa necessario.
        root.update_idletasks()
        contenuto_h = inner.winfo_reqheight()
        schermo_h   = root.winfo_screenheight()
        margine     = 80   # barra titolo + taskbar
        target_h    = min(contenuto_h, schermo_h - margine)
        root.geometry(f"520x{target_h}")
        # Sgancia il callback: serve solo al primo render
        inner.unbind("<Configure>")
        inner.bind("<Configure>", _on_frame_configure)

    # Aggancia temporaneamente al primo Configure del frame interno
    inner.bind("<Configure>", _adatta_altezza)

    # Intestazione
    nomi_browser = [n for n, _ in core.BROWSER_DISPONIBILI]
    tk.Label(inner, text="🔗",
             font=("monospace", 28),
             bg=T["BG"], fg=T["ACCENT"]).pack(pady=(24, 0))
    tk.Label(inner, text="Crea Scorciatoia Web",
             font=("monospace", 17, "bold"),
             bg=T["BG"], fg=T["FG"]).pack(pady=(4, 2))
    tk.Label(inner,
             text=f"Browser rilevati: {', '.join(nomi_browser) or 'nessuno'}",
             font=("monospace", 9),
             bg=T["BG"], fg=T["GREEN"]).pack(pady=(0, 8))

    # Frame campi input
    frame = tk.Frame(inner, bg=T["CARD"], padx=28, pady=24)
    frame.pack(padx=20, pady=(4, 12), fill="x")

    _make_label(frame, "NOME SCORCIATOIA").pack(fill="x", pady=(0, 4))
    e_nome = _make_entry_con_placeholder(frame, "es. YouTube")
    e_nome.pack(fill="x", ipady=6)

    _make_label(frame, "URL DEL SITO").pack(fill="x", pady=(16, 4))
    e_url = _make_entry_con_placeholder(frame, "https://")
    e_url.pack(fill="x", ipady=6)

    _make_label(frame, f"ICONA — nome file da {core.ICONS_PATH}").pack(fill="x", pady=(16, 4))
    icona_row = tk.Frame(frame, bg=T["CARD"])
    icona_row.pack(fill="x")
    e_icona = _make_entry_con_placeholder(icona_row, "es. youtube.png  (opzionale)")
    e_icona.pack(side="left", fill="x", expand=True, ipady=6)
    _make_btn_cartella(icona_row).pack(side="left", padx=(6, 0))

    _make_label(frame, "BROWSER").pack(fill="x", pady=(16, 4))
    opzioni = nomi_browser if nomi_browser else ["Nessun browser rilevato"]
    browser_var = tk.StringVar(value=opzioni[0])
    _make_option_menu(frame, browser_var, opzioni).pack(fill="x", ipady=4)

    # Label stato
    stato_var = tk.StringVar()
    tk.Label(inner, textvariable=stato_var,
             font=("monospace", 10),
             bg=T["BG"], fg=T["GREEN"], wraplength=480).pack(pady=6)

    # Pulsante crea
    tk.Button(
        inner, text="✚   CREA SCORCIATOIA",
        font=("monospace", 13, "bold"),
        bg=T["ACCENT"], fg="white",
        activebackground="#6d28d9", activeforeground="white",
        relief="flat", bd=0, padx=24, pady=14, cursor="hand2",
        command=lambda: _on_crea(e_nome, e_url, e_icona, browser_var, stato_var, root)
    ).pack(pady=(0, 24))


# ══════════════════════════════════════════════════════════════
# PARTE 8 — AVVIO GUI
# Funzione pubblica chiamata da scorcy.py.
# ══════════════════════════════════════════════════════════════

def avvia():
    root = tk.Tk()
    _costruisci_finestra(root)
    root.mainloop()
