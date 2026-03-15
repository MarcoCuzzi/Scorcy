#!/usr/bin/env python3
"""
ui_gui.py — Modalità GUI (tkinter) di Scorcy (Linux).
Costruisce la finestra principale e la finestra impostazioni.
Delega tutta la logica di creazione a core.py e la
configurazione persistente a config.py.
"""

import tkinter as tk
from tkinter import messagebox
import core
import config as cfg


# ══════════════════════════════════════════════════════════════
# PARTE 1 — TEMA VISIVO
# Dizionario centralizzato con tutti i colori dell'interfaccia.
# Modificare qui per cambiare l'aspetto dell'intera GUI
# senza toccare il codice dei widget.
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
    "ORANGE":       "#fb923c",
    "RED":          "#f87171",
    "PINK":         "#f472b6",
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
# ══════════════════════════════════════════════════════════════

class _ScrollbarCustom(tk.Canvas):
    LARGHEZZA    = 16
    RAGGIO_THUMB = 8
    RAGGIO_TRACK = 8
    PADDING      = 3
    THUMB_HOVER  = "#7c3aed"

    def __init__(self, parent, canvas_target: tk.Canvas, **kwargs):
        super().__init__(
            parent,
            width=self.LARGHEZZA,
            bg=THEME["BG"],
            highlightthickness=0,
            **kwargs
        )
        self._canvas = canvas_target
        self._drag_y = None
        self._canvas.configure(yscrollcommand=self._aggiorna)
        self.bind("<Configure>",       self._ridisegna)
        self.bind("<ButtonPress-1>",   self._on_click)
        self.bind("<B1-Motion>",       self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>",           self._on_enter)
        self.bind("<Leave>",           self._on_leave)

    def _aggiorna(self, primo: str, secondo: str):
        self._top    = float(primo)
        self._bottom = float(secondo)
        self._ridisegna()

    def _rrect(self, x0, y0, x1, y1, r, colore):
        self.create_arc(x0,       y0,       x0+r*2, y0+r*2, start=90,  extent=90,  fill=colore, outline="")
        self.create_arc(x1-r*2,   y0,       x1,     y0+r*2, start=0,   extent=90,  fill=colore, outline="")
        self.create_arc(x0,       y1-r*2,   x0+r*2, y1,     start=180, extent=90,  fill=colore, outline="")
        self.create_arc(x1-r*2,   y1-r*2,   x1,     y1,     start=270, extent=90,  fill=colore, outline="")
        self.create_rectangle(x0+r, y0,     x1-r, y1,     fill=colore, outline="")
        self.create_rectangle(x0,   y0+r,   x1,   y1-r,   fill=colore, outline="")

    def _ridisegna(self, _=None):
        self.delete("all")
        h = self.winfo_height()
        w = self.winfo_width()
        if h < 2:
            return
        p = self.PADDING
        self._rrect(p, p, w-p, h-p, self.RAGGIO_TRACK, THEME["SCROLL_TRACK"])
        top    = getattr(self, "_top",    0.0)
        bottom = getattr(self, "_bottom", 1.0)
        if top <= 0.0 and bottom >= 1.0:
            return
        track_h = h - p * 2
        y0 = p + top    * track_h + p
        y1 = p + bottom * track_h - p
        y1 = max(y1, y0 + self.RAGGIO_THUMB * 2)
        colore = getattr(self, "_colore_thumb", THEME["SCROLL_THUMB"])
        self._rrect(p+1, y0, w-p-1, y1, self.RAGGIO_THUMB, colore)

    def _on_click(self, event):   self._drag_y = event.y
    def _on_release(self, event): self._drag_y = None
    def _on_enter(self, _):
        self._colore_thumb = self.THUMB_HOVER; self._ridisegna()
    def _on_leave(self, _):
        self._colore_thumb = THEME["SCROLL_THUMB"]; self._ridisegna()

    def _on_drag(self, event):
        if self._drag_y is None:
            return
        h     = self.winfo_height()
        delta = (event.y - self._drag_y) / h
        self._drag_y = event.y
        self._canvas.yview_moveto(getattr(self, "_top", 0.0) + delta)


# ══════════════════════════════════════════════════════════════
# PARTE 3 — WIDGET HELPERS
# Funzioni riutilizzabili per creare i widget standard
# dell'interfaccia con lo stile del tema applicato.
# ══════════════════════════════════════════════════════════════

def _make_label(parent, testo: str, **kw) -> tk.Label:
    return tk.Label(
        parent, text=testo,
        font=("monospace", 11, "bold"),
        bg=kw.get("bg", THEME["CARD"]),
        fg=THEME["FG"], anchor="w"
    )

def _make_entry_con_placeholder(parent, placeholder: str,
                                 bg: str | None = None) -> tk.Entry:
    e = tk.Entry(
        parent,
        font=("monospace", 11),
        bg=bg or THEME["ENTRY_BG"], fg=THEME["MUTED"],
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
    """Pulsante giallo 📂 che apre ICONS_PATH nel file manager."""
    btn = tk.Frame(parent, bg=THEME["YELLOW"], cursor="hand2")
    tk.Label(btn, text="📂", font=("monospace", 11),
             bg=THEME["YELLOW"], fg="#1e1e2e").pack(padx=6, pady=(3, 0))
    tk.Label(btn, text="apri", font=("monospace", 7),
             bg=THEME["YELLOW"], fg="#1e1e2e").pack(padx=6, pady=(0, 3))
    btn.bind("<Button-1>", lambda _: core.apri_cartella_icone())
    for child in btn.winfo_children():
        child.bind("<Button-1>", lambda _: core.apri_cartella_icone())
    return btn

def _make_option_menu(parent, var: tk.StringVar,
                      opzioni: list[str]) -> tk.OptionMenu:
    T = THEME
    opzioni_emoji = [f"{_emoji_browser(n)}  {n}" for n in opzioni]
    var.set(opzioni_emoji[0] if opzioni_emoji else "")
    menu = tk.OptionMenu(parent, var, *opzioni_emoji)
    menu.config(
        font=("monospace", 11), bg=T["ENTRY_BG"], fg=T["FG"],
        activebackground=T["ACCENT"], activeforeground="white",
        highlightthickness=0, relief="flat", bd=0, anchor="w",
        indicatoron=True
    )
    menu["menu"].config(
        font=("monospace", 11), bg=T["ENTRY_BG"], fg=T["FG"],
        activebackground=T["ACCENT"], activeforeground="white"
    )
    return menu


# ══════════════════════════════════════════════════════════════
# PARTE 4 — LETTURA E RESET ENTRY
# _leggi_entry restituisce il valore reale ignorando il
# placeholder. _reset_entry riporta il campo allo stato
# iniziale con il placeholder e il colore muted.
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
# Controlla nome e URL prima di passare il controllo a core.
# Ritorna una stringa di errore se qualcosa non va, None
# se tutto è valido.
# ══════════════════════════════════════════════════════════════

def _valida_input(nome: str, url: str) -> tuple[str | None, str | None]:
    """
    Restituisce (errore_nome, errore_url).
    errore_nome: non ignorabile (nome vuoto o invalido).
    errore_url:  ignorabile tramite il tasto Ignora.
    """
    nome_pulito = core.sanitizza_nome(nome)
    if not nome_pulito:
        return "Inserisci un nome valido per la scorciatoia.", None
    if not url or url == "https://":
        return None, "Inserisci un URL valido."
    url_norm   = core.normalizza_url(url)
    errore_url = core.valida_url(url_norm)
    return None, errore_url


def _dialog_url_warning(messaggio: str, parent: tk.Tk) -> bool:
    """
    Dialog con Correggi e Ignora.
    Restituisce True se l'utente vuole ignorare e procedere.
    """
    T      = THEME
    result = [False]
    dlg    = tk.Toplevel(parent)
    dlg.title("URL non valido")
    dlg.configure(bg=T["BG"])
    dlg.resizable(False, False)
    dlg.grab_set()
    dlg.transient(parent)

    tk.Label(dlg, text="\u26a0\ufe0f",
             font=("monospace", 42),
             bg=T["BG"], fg=T["YELLOW"]).pack(pady=(24, 6))

    tk.Label(dlg, text=messaggio,
             font=("monospace", 13),
             bg=T["BG"], fg=T["FG"],
             wraplength=360, justify="center").pack(padx=28, pady=(0, 24))

    btn_row = tk.Frame(dlg, bg=T["BG"])
    btn_row.pack(pady=(0, 24), padx=28)

    def _correggi():
        result[0] = False
        dlg.destroy()

    def _ignora():
        result[0] = True
        dlg.destroy()

    tk.Button(btn_row, text="Correggi",
              font=("monospace", 12, "bold"),
              bg=T["ENTRY_BG"], fg=T["FG"],
              activebackground=T["CARD"], activeforeground=T["FG"],
              relief="flat", bd=0, padx=20, pady=10, cursor="hand2",
              command=_correggi).pack(side="left", padx=(0, 10))

    tk.Button(btn_row, text="Ignora",
              font=("monospace", 12, "bold"),
              bg=T["ACCENT"], fg="white",
              activebackground="#6d28d9", activeforeground="white",
              relief="flat", bd=0, padx=20, pady=10, cursor="hand2",
              command=_ignora).pack(side="left")

    dlg.update_idletasks()
    px = parent.winfo_x() + parent.winfo_width()  // 2 - dlg.winfo_reqwidth()  // 2
    py = parent.winfo_y() + parent.winfo_height() // 2 - dlg.winfo_reqheight() // 2
    dlg.geometry(f"+{px}+{py}")
    dlg.wait_window()
    return result[0]


# ══════════════════════════════════════════════════════════════
# PARTE 6 — CALLBACK PULSANTE CREA
# errore_nome blocca sempre. errore_url mostra la dialog
# con Correggi / Ignora: se ignorato, la validazione viene
# disabilitata temporaneamente solo per questa creazione.
# ══════════════════════════════════════════════════════════════

def _on_crea(e_nome, e_url, e_icona, browser_var, stato_var, root):
    nome       = _leggi_entry(e_nome)
    url        = _leggi_entry(e_url)
    icona      = _leggi_entry(e_icona)
    nome_b_sel = browser_var.get().split("  ", 1)[-1]
    browser_exe = next(
        (exe for n, exe in core.BROWSER_DISPONIBILI if n == nome_b_sel), ""
    )

    errore_nome, errore_url = _valida_input(nome, url)

    if errore_nome:
        messagebox.showwarning("Attenzione", errore_nome, parent=root)
        return

    ignora_url = False
    if errore_url:
        ignora_url = _dialog_url_warning(errore_url, root)
        if not ignora_url:
            return  # utente vuole correggere

    def _esegui(sovrascrittura=False):
        import config as cfg
        if ignora_url:
            cfg.set("url_validation", False)
        try:
            if sovrascrittura:
                s = core.sovrascrivi_scorciatoia(nome, url, icona, browser_exe)
            else:
                s = core.crea_scorciatoia(nome, url, icona, browser_exe)
        finally:
            if ignora_url:
                cfg.set("url_validation", True)
        azione = "sovrascritta" if sovrascrittura else "creata"
        stato_var.set(f"✅ '{nome}' {azione} con {s.nome_browser} sul Desktop!")
        for e in (e_nome, e_url, e_icona):
            _reset_entry(e)

    try:
        _esegui()
    except ValueError as exc:
        messagebox.showwarning("Attenzione", str(exc), parent=root)
    except FileExistsError:
        nome_file = core.nome_a_filename(core.sanitizza_nome(nome))
        if messagebox.askyesno(
            "File esistente",
            f"Esiste già '{nome_file}'.\nSovrascrivere?",
            parent=root
        ):
            _esegui(sovrascrittura=True)


# ══════════════════════════════════════════════════════════════
# PARTE 7 — FINESTRA IMPOSTAZIONI
# Finestra indipendente (Toplevel) aperta dal pulsante ⚙️.
# Mostra tre impostazioni: validazione URL (Checkbutton),
# browser default (OptionMenu), cartella icone (Entry + 📂).
# Le modifiche hanno effetto solo dopo "Salva".
# Alla chiusura, se ci sono modifiche non salvate, chiede
# conferma prima di uscire.
# ══════════════════════════════════════════════════════════════

def _apri_impostazioni(parent: tk.Tk):
    T   = THEME
    win = tk.Toplevel(parent)
    win.title("Impostazioni — Scorcy")
    win.configure(bg=T["BG"])
    win.resizable(True, True)
    win.minsize(400, 300)

    # Carica config corrente
    conf_corrente = cfg.carica()

    # ── Variabili tkinter ──────────────────────────────────────
    var_validazione    = tk.BooleanVar(value=conf_corrente.get("url_validation",   True))
    var_raggiungibilita = tk.BooleanVar(value=conf_corrente.get("url_reachability", True))
    var_name_val       = tk.BooleanVar(value=conf_corrente.get("name_validation",  True))
    var_name_dup       = tk.BooleanVar(value=conf_corrente.get("name_duplicate",   True))
    var_icon_check     = tk.BooleanVar(value=conf_corrente.get("icon_check",       True))
    var_composite      = tk.BooleanVar(value=conf_corrente.get("composite_icon",  True))

    nomi_browser   = [n for n, _ in core.BROWSER_DISPONIBILI]
    exe_browser    = [e for _, e in core.BROWSER_DISPONIBILI]
    default_exe    = conf_corrente.get("browser_default", "")
    default_idx    = exe_browser.index(default_exe) if default_exe in exe_browser else 0
    opzioni_menu   = [f"{_emoji_browser(n)}  {n}" for n in nomi_browser] or ["Nessun browser rilevato"]
    var_browser    = tk.StringVar(value=opzioni_menu[default_idx] if opzioni_menu else "")

    var_icons_path = tk.StringVar(value=conf_corrente.get("icons_path", ""))

    # Tiene traccia se ci sono modifiche non salvate
    def _modificato() -> bool:
        nome_sel = var_browser.get().split("  ", 1)[-1]
        exe_sel  = next((e for n, e in core.BROWSER_DISPONIBILI if n == nome_sel), "")
        return (
            var_validazione.get()     != conf_corrente.get("url_validation")   or
            var_raggiungibilita.get() != conf_corrente.get("url_reachability") or
            var_name_val.get()        != conf_corrente.get("name_validation")  or
            var_name_dup.get()        != conf_corrente.get("name_duplicate")   or
            var_icon_check.get()      != conf_corrente.get("icon_check")        or
            var_composite.get()       != conf_corrente.get("composite_icon")     or
            exe_sel                   != conf_corrente.get("browser_default")  or
            var_icons_path.get()      != conf_corrente.get("icons_path")
        )

    # ── Canvas scrollabile (stessa struttura della finestra principale) ────
    canvas    = tk.Canvas(win, bg=T["BG"], highlightthickness=0)
    scrollbar = _ScrollbarCustom(win, canvas_target=canvas)
    canvas.configure(yscrollcommand=scrollbar._aggiorna)
    scrollbar.pack(side="right", fill="y", padx=(2, 4), pady=8)
    canvas.pack(side="left", fill="both", expand=True)

    inner    = tk.Frame(canvas, bg=T["BG"])
    inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")

    def _on_frame_configure(_):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _on_canvas_configure(event):
        canvas.itemconfig(inner_id, width=event.width)

    canvas.bind("<Configure>", _on_canvas_configure)

    # Scroll rotella — bind sul canvas locale, non bind_all, per evitare
    # che i callback sopravvivano alla chiusura della finestra impostazioni.
    def _scroll_su(e):
        try: canvas.yview_scroll(-1, "units")
        except Exception: pass
    def _scroll_giu(e):
        try: canvas.yview_scroll(1, "units")
        except Exception: pass

    id4 = canvas.bind_all("<Button-4>", _scroll_su)
    id5 = canvas.bind_all("<Button-5>", _scroll_giu)

    # Rimuove i bind globali quando la finestra viene distrutta
    def _on_destroy(_=None):
        try:
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
        except Exception:
            pass
    win.bind("<Destroy>", _on_destroy)

    # Adatta altezza finestra al contenuto al primo render
    def _adatta_altezza(_=None):
        win.update_idletasks()
        contenuto_h = inner.winfo_reqheight()
        schermo_h   = win.winfo_screenheight()
        margine     = 80
        target_h    = min(contenuto_h + 20, schermo_h - margine)
        win.geometry(f"480x{target_h}")
        inner.unbind("<Configure>")
        inner.bind("<Configure>", _on_frame_configure)

    inner.bind("<Configure>", _adatta_altezza)

    # ── Layout — intestazione con rotellina e titolo affiancati ──
    header = tk.Frame(inner, bg=T["BG"])
    header.pack(pady=(28, 4))

    tk.Label(header, text="⚙️",
             font=("monospace", 26),
             bg=T["BG"], fg=T["MUTED"]).pack(side="left", padx=(0, 10))

    tk.Label(header, text="Impostazioni",
             font=("monospace", 22, "bold"),
             bg=T["BG"], fg=T["FG"]).pack(side="left")

    tk.Label(inner, text="Le modifiche hanno effetto solo dopo aver cliccato Salva.",
             font=("monospace", 11, "bold"),
             bg=T["BG"], fg=T["MUTED"], wraplength=440).pack(pady=(4, 16))

    frame = tk.Frame(inner, bg=T["CARD"], padx=28, pady=20)
    frame.pack(padx=20, pady=(0, 4), fill="x")

    # — Validazione URL —
    tk.Label(frame, text="VALIDAZIONE URL",
             font=("monospace", 10, "bold"),
             bg=T["CARD"], fg=T["FG"], anchor="w").pack(fill="x", pady=(0, 6))

    # Riga con Checkbutton + label colorata verde/rosso
    row_val = tk.Frame(frame, bg=T["CARD"])
    row_val.pack(fill="x", pady=(0, 16))

    colore_val = T["GREEN"] if var_validazione.get() else T["RED"]
    lbl_val = tk.Label(row_val, text="Controllo sintassi URL",
                       font=("monospace", 11, "bold"),
                       bg=T["CARD"], fg=colore_val)
    lbl_val.pack(side="left", padx=(0, 10))

    def _aggiorna_colore_val():
        lbl_val.config(fg=T["GREEN"] if var_validazione.get() else T["RED"])

    tk.Checkbutton(
        row_val,
        variable=var_validazione,
        font=("monospace", 10),
        bg=T["CARD"], fg=T["FG"],
        selectcolor=T["ENTRY_BG"],
        activebackground=T["CARD"],
        activeforeground=T["FG"],
        command=_aggiorna_colore_val
    ).pack(side="left")

    # — Raggiungibilità URL —
    tk.Label(frame, text="RAGGIUNGIBILITÀ URL",
             font=("monospace", 10, "bold"),
             bg=T["CARD"], fg=T["FG"], anchor="w").pack(fill="x", pady=(0, 6))

    row_reach = tk.Frame(frame, bg=T["CARD"])
    row_reach.pack(fill="x", pady=(0, 16))

    colore_reach = T["GREEN"] if var_raggiungibilita.get() else T["RED"]
    lbl_reach = tk.Label(row_reach, text="Controllo raggiungibilità URL",
                         font=("monospace", 11, "bold"),
                         bg=T["CARD"], fg=colore_reach)
    lbl_reach.pack(side="left", padx=(0, 10))

    def _aggiorna_colore_reach():
        lbl_reach.config(fg=T["GREEN"] if var_raggiungibilita.get() else T["RED"])

    tk.Checkbutton(
        row_reach,
        variable=var_raggiungibilita,
        font=("monospace", 10),
        bg=T["CARD"], fg=T["FG"],
        selectcolor=T["ENTRY_BG"],
        activebackground=T["CARD"],
        activeforeground=T["FG"],
        command=_aggiorna_colore_reach
    ).pack(side="left")

    # — Validazione nome —
    tk.Label(frame, text="NOME SCORCIATOIA",
             font=("monospace", 10, "bold"),
             bg=T["CARD"], fg=T["FG"], anchor="w").pack(fill="x", pady=(0, 6))

    row_name_val = tk.Frame(frame, bg=T["CARD"])
    row_name_val.pack(fill="x")
    lbl_name_val = tk.Label(row_name_val, text="Controllo sintassi nome",
                            font=("monospace", 11, "bold"),
                            bg=T["CARD"],
                            fg=T["GREEN"] if var_name_val.get() else T["RED"])
    lbl_name_val.pack(side="left", padx=(0, 10))
    def _aggiorna_name_val():
        lbl_name_val.config(fg=T["GREEN"] if var_name_val.get() else T["RED"])
    tk.Checkbutton(row_name_val, variable=var_name_val,
                   font=("monospace", 10), bg=T["CARD"], fg=T["FG"],
                   selectcolor=T["ENTRY_BG"], activebackground=T["CARD"],
                   activeforeground=T["FG"],
                   command=_aggiorna_name_val).pack(side="left")

    row_name_dup = tk.Frame(frame, bg=T["CARD"])
    row_name_dup.pack(fill="x", pady=(10, 16))
    lbl_name_dup = tk.Label(row_name_dup, text="Controllo nome duplicato",
                            font=("monospace", 11, "bold"),
                            bg=T["CARD"],
                            fg=T["GREEN"] if var_name_dup.get() else T["RED"])
    lbl_name_dup.pack(side="left", padx=(0, 10))
    def _aggiorna_name_dup():
        lbl_name_dup.config(fg=T["GREEN"] if var_name_dup.get() else T["RED"])
    tk.Checkbutton(row_name_dup, variable=var_name_dup,
                   font=("monospace", 10), bg=T["CARD"], fg=T["FG"],
                   selectcolor=T["ENTRY_BG"], activebackground=T["CARD"],
                   activeforeground=T["FG"],
                   command=_aggiorna_name_dup).pack(side="left")

    # — Controllo icona —
    tk.Label(frame, text="ICONA",
             font=("monospace", 10, "bold"),
             bg=T["CARD"], fg=T["FG"], anchor="w").pack(fill="x", pady=(0, 6))

    row_icon = tk.Frame(frame, bg=T["CARD"])
    row_icon.pack(fill="x", pady=(0, 16))
    lbl_icon = tk.Label(row_icon, text="Controllo esistenza icona",
                        font=("monospace", 11, "bold"),
                        bg=T["CARD"],
                        fg=T["GREEN"] if var_icon_check.get() else T["RED"])
    lbl_icon.pack(side="left", padx=(0, 10))
    def _aggiorna_icon_check():
        lbl_icon.config(fg=T["GREEN"] if var_icon_check.get() else T["RED"])
    tk.Checkbutton(row_icon, variable=var_icon_check,
                   font=("monospace", 10), bg=T["CARD"], fg=T["FG"],
                   selectcolor=T["ENTRY_BG"], activebackground=T["CARD"],
                   activeforeground=T["FG"],
                   command=_aggiorna_icon_check).pack(side="left")

    # — Icona composita —
    tk.Label(frame, text="ICONA COMPOSITA",
             font=("monospace", 10, "bold"),
             bg=T["CARD"], fg=T["FG"], anchor="w").pack(fill="x", pady=(0, 6))

    row_comp = tk.Frame(frame, bg=T["CARD"])
    row_comp.pack(fill="x", pady=(0, 4))

    import core as _core_ref
    pillow_ok = _core_ref.PILLOW_DISPONIBILE

    # Colore: verde=attivo+Pillow, rosso=disattivo, giallo=attivo ma Pillow mancante
    def _colore_comp():
        if not var_composite.get():
            return T["RED"]
        return T["GREEN"] if pillow_ok else T["YELLOW"]

    lbl_comp = tk.Label(row_comp, text="Badge browser sull'icona",
                        font=("monospace", 11, "bold"),
                        bg=T["CARD"], fg=_colore_comp())
    lbl_comp.pack(side="left", padx=(0, 10))

    def _aggiorna_comp():
        lbl_comp.config(fg=_colore_comp())

    tk.Checkbutton(row_comp, variable=var_composite,
                   font=("monospace", 10), bg=T["CARD"], fg=T["FG"],
                   selectcolor=T["ENTRY_BG"], activebackground=T["CARD"],
                   activeforeground=T["FG"],
                   command=_aggiorna_comp).pack(side="left")

    if not pillow_ok:
        tk.Label(frame, text="⚠️  Pillow non installato — sudo apt install python3-pil",
                 font=("monospace", 8),
                 bg=T["CARD"], fg=T["YELLOW"]).pack(anchor="w", pady=(0, 12))
    else:
        tk.Frame(frame, height=12, bg=T["CARD"]).pack()

    # — Browser default —
    tk.Label(frame, text="BROWSER PREDEFINITO",
             font=("monospace", 10, "bold"),
             bg=T["CARD"], fg=T["FG"], anchor="w").pack(fill="x", pady=(0, 6))
    if nomi_browser:
        # Riga: icona browser + OptionMenu affiancati
        row_browser = tk.Frame(frame, bg=T["CARD"])
        row_browser.pack(fill="x", ipady=4)

        # Precarica le icone PNG di sistema per tutti i browser disponibili
        # Le immagini devono essere tenute in un dict per evitare che il GC le elimini
        _img_cache: dict[str, tk.PhotoImage] = {}
        for _n in nomi_browser:
            _p = core.cerca_icona_browser(_n)
            if _p:
                try:
                    _img_cache[_n] = tk.PhotoImage(file=_p)
                except Exception:
                    pass

        # Label icona — aggiornata al cambio selezione
        lbl_icona_browser = tk.Label(row_browser, bg=T["CARD"])
        lbl_icona_browser.pack(side="left", padx=(0, 8))

        def _aggiorna_icona_browser(*_):
            nome_sel = var_browser.get().split("  ", 1)[-1]
            img = _img_cache.get(nome_sel)
            if img:
                lbl_icona_browser.config(image=img, text="")
            else:
                lbl_icona_browser.config(image="", text=_emoji_browser(nome_sel),
                                         font=("monospace", 20))

        var_browser.trace_add("write", _aggiorna_icona_browser)
        _aggiorna_icona_browser()  # imposta l'icona del browser default al primo render

        _make_option_menu(row_browser, var_browser, nomi_browser).pack(
            side="left", fill="x", expand=True, ipady=4)
    else:
        tk.Label(frame, text="Nessun browser rilevato",
                 font=("monospace", 10), bg=T["CARD"], fg=T["MUTED"]).pack(anchor="w")

    # — Cartella icone —
    tk.Label(frame, text="CARTELLA ICONE",
             font=("monospace", 10, "bold"),
             bg=T["CARD"], fg=T["FG"], anchor="w").pack(fill="x", pady=(16, 6))
    row_icone = tk.Frame(frame, bg=T["CARD"])
    row_icone.pack(fill="x")
    tk.Entry(
        row_icone,
        textvariable=var_icons_path,
        font=("monospace", 10),
        bg=T["ENTRY_BG"], fg=T["FG"],
        insertbackground=T["FG"],
        relief="flat", bd=6
    ).pack(side="left", fill="x", expand=True, ipady=5)

    def _apri_cartella_corrente():
        import subprocess, os
        path = var_icons_path.get().strip()
        os.makedirs(path, exist_ok=True)
        try:
            subprocess.Popen(["xdg-open", path])
        except Exception:
            pass

    btn_apri = tk.Frame(row_icone, bg=T["YELLOW"], cursor="hand2")
    tk.Label(btn_apri, text="📂", font=("monospace", 11),
             bg=T["YELLOW"], fg="#1e1e2e").pack(padx=6, pady=(3, 0))
    tk.Label(btn_apri, text="apri", font=("monospace", 7),
             bg=T["YELLOW"], fg="#1e1e2e").pack(padx=6, pady=(0, 3))
    btn_apri.pack(side="left", padx=(6, 0))
    btn_apri.bind("<Button-1>", lambda _: _apri_cartella_corrente())
    for child in btn_apri.winfo_children():
        child.bind("<Button-1>", lambda _: _apri_cartella_corrente())

    # ── Label stato salvataggio ────────────────────────────────
    stato_var = tk.StringVar()
    tk.Label(inner, textvariable=stato_var,
             font=("monospace", 9),
             bg=T["BG"], fg=T["GREEN"]).pack(pady=(12, 0))

    # ── Pulsante Salva ─────────────────────────────────────────
    def _salva():
        nome_sel    = var_browser.get().split("  ", 1)[-1]
        exe_sel     = next((e for n, e in core.BROWSER_DISPONIBILI if n == nome_sel), "")
        icons_input = var_icons_path.get().strip()
        nuova_conf  = {
            "url_validation":   var_validazione.get(),
            "url_reachability": var_raggiungibilita.get(),
            "name_validation":  var_name_val.get(),
            "name_duplicate":   var_name_dup.get(),
            "icon_check":       var_icon_check.get(),
            "composite_icon":   var_composite.get(),
            "browser_default":  exe_sel,
            "icons_path":       icons_input,
        }
        cfg.salva(nuova_conf)
        conf_corrente.update(nuova_conf)
        stato_var.set("✅ Impostazioni salvate.")

    tk.Button(
        inner, text="💾  Salva",
        font=("monospace", 12, "bold"),
        bg=T["ACCENT"], fg="white",
        activebackground="#6d28d9", activeforeground="white",
        relief="flat", bd=0, padx=24, pady=12, cursor="hand2",
        command=_salva
    ).pack(pady=(8, 24))

    # ── Gestione chiusura con modifiche non salvate ────────────
    def _on_close():
        if _modificato():
            risposta = messagebox.askyesnocancel(
                "Modifiche non salvate",
                "Hai modifiche non salvate.\nVuoi salvarle prima di chiudere?",
                parent=win
            )
            if risposta is True:
                _salva()
                win.destroy()
            elif risposta is False:
                win.destroy()
            # None = Cancel → non chiude
        else:
            win.destroy()

    win.protocol("WM_DELETE_WINDOW", _on_close)


# ══════════════════════════════════════════════════════════════
# PARTE 8 — COSTRUZIONE FINESTRA PRINCIPALE
# Assembla tutti i widget nella finestra principale.
# Il pulsante ⚙️ in alto a destra apre la finestra impostazioni.
# ══════════════════════════════════════════════════════════════

def _costruisci_finestra(root: tk.Tk):
    T = THEME
    root.title("Scorcy")
    root.resizable(True, True)
    root.minsize(400, 300)
    root.configure(bg=T["BG"])

    # Canvas principale con scrollbar custom
    canvas = tk.Canvas(root, bg=T["BG"], highlightthickness=0)
    scrollbar = _ScrollbarCustom(root, canvas_target=canvas)
    canvas.configure(yscrollcommand=scrollbar._aggiorna)
    scrollbar.pack(side="right", fill="y", padx=(2, 4), pady=8)
    canvas.pack(side="left", fill="both", expand=True)

    inner    = tk.Frame(canvas, bg=T["BG"])
    inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")

    def _on_frame_configure(_):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _on_canvas_configure(event):
        canvas.itemconfig(inner_id, width=event.width)

    canvas.bind("<Configure>", _on_canvas_configure)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

    def _adatta_altezza(_=None):
        root.update_idletasks()
        contenuto_h = inner.winfo_reqheight()
        schermo_h   = root.winfo_screenheight()
        margine     = 80
        target_h    = min(contenuto_h, schermo_h - margine)
        root.geometry(f"520x{target_h}")
        # Dopo il primo render ripristina il bind normale con posizionamento ⚙️
        inner.unbind("<Configure>")
        inner.bind("<Configure>", lambda e: (_on_frame_configure(e), _piazza_settings()))
        _piazza_settings()

    # ── Pulsante ⚙️ — posizionato con place nell'angolo in alto a destra ──
    btn_settings = tk.Button(
        inner, text="⚙️",
        font=("monospace", 26),
        bg=T["BG"], fg=T["MUTED"],
        activebackground=T["BG"], activeforeground=T["FG"],
        relief="flat", bd=0, highlightthickness=0,
        cursor="hand2",
        command=lambda: _apri_impostazioni(root)
    )

    # ── Intestazione centrata ──────────────────────────────────
    tk.Label(inner, text="🔗",
             font=("monospace", 52),
             bg=T["BG"], fg=T["ACCENT"]).pack(pady=(36, 0))

    tk.Label(inner, text="Crea Scorciatoia Web",
             font=("monospace", 19, "bold"),
             bg=T["BG"], fg=T["FG"]).pack(pady=(6, 2))

    nomi_browser = [n for n, _ in core.BROWSER_DISPONIBILI]
    tk.Label(inner,
             text=f"Browser rilevati: {', '.join(nomi_browser) or 'nessuno'}",
             font=("monospace", 10, "bold"),
             bg=T["BG"], fg=T["GREEN"]).pack(pady=(0, 14))

    # ── Frame campi input ──────────────────────────────────────
    frame = tk.Frame(inner, bg=T["CARD"], padx=28, pady=24)
    frame.pack(padx=20, pady=(4, 12), fill="x")

    _make_label(frame, "NOME SCORCIATOIA").pack(fill="x", pady=(0, 4))

    # Bordo colorato — neutro/giallo/rosso/rosa
    nome_border = tk.Frame(frame, bg=T["ENTRY_BG"], padx=2, pady=2)
    nome_border.pack(fill="x")
    e_nome = _make_entry_con_placeholder(nome_border, "es. YouTube")
    e_nome.pack(fill="x", ipady=6)

    # ── Controllo nome in background ──────────────────────────
    _nome_check_id = [None]

    def _imposta_bordo_nome(colore):
        nome_border.config(bg=colore)

    def _controlla_nome_thread(nome_da_controllare):
        import os
        percorso = os.path.join(
            core.DESKTOP_PATH,
            core.nome_a_filename(nome_da_controllare)
        )
        if os.path.exists(percorso):
            root.after(0, lambda: _imposta_bordo_nome(T["PINK"]))
        else:
            root.after(0, lambda: _imposta_bordo_nome(T["GREEN"]))

    def _on_nome_modifica(*_):
        if _nome_check_id[0]:
            root.after_cancel(_nome_check_id[0])
            _nome_check_id[0] = None

        nome_raw  = e_nome.get().strip()
        placeholder = getattr(e_nome, "_placeholder", "")

        # Campo vuoto o placeholder — bordo neutro
        if not nome_raw or nome_raw == placeholder:
            _imposta_bordo_nome(T["ENTRY_BG"])
            return

        # Controllo sintassi (istantaneo, nessun thread)
        if cfg.get("name_validation"):
            nome_pulito = core.sanitizza_nome(nome_raw)
            if not nome_pulito:
                _imposta_bordo_nome(T["RED"])
                return
            if len(nome_raw) > 200:
                _imposta_bordo_nome(T["RED"])
                return
            if nome_raw != nome_pulito:
                # Contiene caratteri che verranno rimossi — avvisa in rosso
                _imposta_bordo_nome(T["RED"])
                return

        # Controllo duplicato (asincrono con debounce)
        if cfg.get("name_duplicate"):
            _imposta_bordo_nome(T["YELLOW"])
            def _lancia():
                import threading
                threading.Thread(
                    target=_controlla_nome_thread,
                    args=(core.sanitizza_nome(nome_raw),),
                    daemon=True
                ).start()
            _nome_check_id[0] = root.after(800, _lancia)
        else:
            _imposta_bordo_nome(T["GREEN"])

    e_nome.bind("<KeyRelease>", _on_nome_modifica)

    _make_label(frame, "URL DEL SITO").pack(fill="x", pady=(16, 4))

    # Bordo colorato simulato con un Frame wrapper da 2px
    # Colori: ENTRY_BG=neutro, YELLOW=controllo, GREEN=ok, RED=errore
    url_border = tk.Frame(frame, bg=T["ENTRY_BG"], padx=2, pady=2)
    url_border.pack(fill="x")
    e_url = _make_entry_con_placeholder(url_border, "https://")
    e_url.pack(fill="x", ipady=6)

    # ── Controllo raggiungibilità URL in background ────────────
    # Debounce: aspetta 1s dopo l'ultima modifica prima di sparare
    # il thread. Il thread chiama root.after(0, ...) per aggiornare
    # il colore sul thread principale senza bloccare la GUI.
    _url_check_id = [None]   # id del after() pendente

    def _imposta_bordo(colore):
        url_border.config(bg=colore)

    def _controlla_url_thread(url_da_controllare):
        import urllib.request
        try:
            req = urllib.request.Request(
                url_da_controllare,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            urllib.request.urlopen(req, timeout=4)
            root.after(0, lambda: _imposta_bordo(T["GREEN"]))
        except Exception:
            root.after(0, lambda: _imposta_bordo(T["RED"]))

    def _on_url_modifica(*_):
        # Cancella il timer precedente se l'utente sta ancora scrivendo
        if _url_check_id[0]:
            root.after_cancel(_url_check_id[0])
            _url_check_id[0] = None

        url_raw = e_url.get().strip()
        placeholder = getattr(e_url, "_placeholder", "")

        # Reset bordo se campo vuoto o placeholder
        if not url_raw or url_raw == placeholder:
            _imposta_bordo(T["ENTRY_BG"])
            return

        # Se il controllo raggiungibilità è disabilitato, bordo neutro e stop
        if not cfg.get("url_reachability"):
            _imposta_bordo(T["ENTRY_BG"])
            return

        url_norm = core.normalizza_url(url_raw)

        # Bordo giallo subito — indica controllo in corso
        _imposta_bordo(T["YELLOW"])

        # Lancia il controllo dopo 1 secondo di inattività
        def _lancia():
            import threading
            threading.Thread(
                target=_controlla_url_thread,
                args=(url_norm,),
                daemon=True
            ).start()

        _url_check_id[0] = root.after(1000, _lancia)

    e_url.bind("<KeyRelease>", _on_url_modifica)

    _make_label(frame, f"ICONA — nome file da {core.ICONS_PATH}").pack(fill="x", pady=(16, 4))
    icona_row = tk.Frame(frame, bg=T["CARD"])
    icona_row.pack(fill="x")

    # Bordo colorato icona: neutro=non scritto, verde=trovata, arancio=non trovata
    icona_border = tk.Frame(icona_row, bg=T["CARD"], padx=2, pady=2)
    icona_border.pack(side="left", fill="x", expand=True)
    e_icona = _make_entry_con_placeholder(icona_border, "es. youtube.png  (opzionale)")
    e_icona.pack(fill="x", ipady=6)
    _make_btn_cartella(icona_row).pack(side="left", padx=(6, 0))

    def _on_icona_modifica(*_):
        valore = e_icona.get().strip()
        placeholder = getattr(e_icona, "_placeholder", "")
        if not valore or valore == placeholder:
            icona_border.config(bg=T["CARD"])
            return
        if not cfg.get("icon_check"):
            icona_border.config(bg=T["CARD"])
            return
        percorso = core.risolvi_icona(valore)
        import os
        if os.path.isfile(percorso):
            icona_border.config(bg=T["GREEN"])
        else:
            icona_border.config(bg=T["YELLOW"])

    e_icona.bind("<KeyRelease>", _on_icona_modifica)

    _make_label(frame, "BROWSER").pack(fill="x", pady=(16, 4))
    opzioni     = nomi_browser if nomi_browser else ["Nessun browser rilevato"]
    browser_var = tk.StringVar(value=opzioni[0])

    # Riga icona + OptionMenu: icona a sinistra grande, menu ridotto a destra
    browser_row = tk.Frame(frame, bg=T["CARD"])
    browser_row.pack(fill="x")

    # Precarica icone browser (stesso meccanismo delle impostazioni)
    _img_cache_main: dict[str, tk.PhotoImage] = {}
    for _n in nomi_browser:
        _p = core.cerca_icona_browser(_n)
        if _p:
            try:
                _img_cache_main[_n] = tk.PhotoImage(file=_p)
            except Exception:
                pass

    lbl_icona_main = tk.Label(browser_row, bg=T["CARD"])
    lbl_icona_main.pack(side="left", padx=(0, 10))

    def _aggiorna_icona_main(*_):
        nome_sel = browser_var.get().split("  ", 1)[-1]
        img = _img_cache_main.get(nome_sel)
        if img:
            lbl_icona_main.config(image=img, text="")
        else:
            lbl_icona_main.config(image="", text=_emoji_browser(nome_sel),
                                  font=("monospace", 20))

    browser_var.trace_add("write", _aggiorna_icona_main)

    _make_option_menu(browser_row, browser_var, opzioni).pack(
        side="right", fill="x", expand=True, ipady=4)

    _aggiorna_icona_main()  # icona del browser default al primo render

    # ── Label stato ────────────────────────────────────────────
    stato_var = tk.StringVar()
    tk.Label(inner, textvariable=stato_var,
             font=("monospace", 10),
             bg=T["BG"], fg=T["GREEN"], wraplength=480).pack(pady=6)

    # ── Pulsante Crea ──────────────────────────────────────────
    tk.Button(
        inner, text="✚   CREA SCORCIATOIA",
        font=("monospace", 13, "bold"),
        bg=T["ACCENT"], fg="white",
        activebackground="#6d28d9", activeforeground="white",
        relief="flat", bd=0, padx=24, pady=14, cursor="hand2",
        command=lambda: _on_crea(e_nome, e_url, e_icona, browser_var, stato_var, root)
    ).pack(pady=(0, 24))

    # Bind Configure: adatta altezza al primo render, poi aggiorna
    # scrollregion e riposiziona il pulsante ⚙️ ad ogni resize.
    def _piazza_settings():
        w = inner.winfo_width()
        if w > 1:
            btn_settings.place(x=w - 44, y=10)

    inner.bind("<Configure>", _adatta_altezza)


# ══════════════════════════════════════════════════════════════
# PARTE 9 — AVVIO GUI
# Funzione pubblica chiamata da scorcy.py.
# ══════════════════════════════════════════════════════════════

def avvia():
    root = tk.Tk()
    _costruisci_finestra(root)
    root.mainloop()
