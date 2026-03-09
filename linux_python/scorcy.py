#!/usr/bin/env python3
"""
Crea scorciatoie web (.desktop) sul desktop di Ubuntu usando Firefox.
Uso: python3 crea_scorciatoia.py
Oppure: python3 crea_scorciatoia.py "YouTube" "https://youtube.com"
"""

import os
import sys
import stat
import subprocess

DESKTOP_PATH = os.path.expanduser("~/Desktop")
ICONS_PATH = "/home/marco/Icons"

def trova_firefox():
    for cmd in ["firefox", "/usr/bin/firefox", "/snap/bin/firefox"]:
        try:
            result = subprocess.run(["which", cmd.split("/")[-1]], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
    return "firefox"

FIREFOX = trova_firefox()

def risolvi_icona(nome_icona):
    """Dato il nome file icona, restituisce il percorso completo o 'firefox' se vuoto."""
    if not nome_icona:
        return "firefox"
    percorso = os.path.join(ICONS_PATH, nome_icona)
    if os.path.isfile(percorso):
        return percorso
    # Prova ad aggiungere estensioni comuni se non specificata
    for ext in [".png", ".svg", ".jpg", ".xpm"]:
        if os.path.isfile(percorso + ext):
            return percorso + ext
    print(f"⚠️  Icona non trovata in {ICONS_PATH}: {nome_icona}")
    print("   Verrà usata l'icona di Firefox come fallback.")
    return "firefox"

def chiedi_sovrascrittura(percorso_file, nome_file, gui=False, parent=None):
    """Restituisce True se si puo procedere, False se si deve annullare."""
    if not os.path.exists(percorso_file):
        return True
    if gui:
        try:
            from tkinter import messagebox
            return messagebox.askyesno(
                "File esistente",
                f"Esiste gia una scorciatoia '{nome_file}'.\nSovrascrivere?",
                parent=parent
            )
        except Exception:
            pass
    risposta = input(f"\u26a0\ufe0f  Esiste gia '{nome_file}'. Sovrascrivere? (s/n): ").strip().lower()
    return risposta == "s"


def crea_file_desktop(nome, url, icona="", gui=False, parent=None):
    os.makedirs(DESKTOP_PATH, exist_ok=True)

    nome_file = nome.replace(" ", "_") + ".desktop"
    percorso_file = os.path.join(DESKTOP_PATH, nome_file)

    if not chiedi_sovrascrittura(percorso_file, nome_file, gui=gui, parent=parent):
        print("\u23ed\ufe0f  Operazione annullata.")
        return None

    icon_value = risolvi_icona(icona)

    contenuto = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={nome}
Comment=Apre {nome} in Firefox
Exec={FIREFOX} "{url}"
Icon={icon_value}
Terminal=false
Categories=Network;WebBrowser;
"""

    with open(percorso_file, "w") as f:
        f.write(contenuto)

    os.chmod(percorso_file,
             stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
             stat.S_IRGRP | stat.S_IXGRP |
             stat.S_IROTH | stat.S_IXOTH)

    try:
        subprocess.run(
            ["gio", "set", percorso_file, "metadata::trusted", "true"],
            capture_output=True
        )
    except Exception:
        pass

    print(f"✅ Scorciatoia creata: {percorso_file}")
    print(f"   → URL:   {url}")
    print(f"   → Icona: {icon_value}")
    return percorso_file


def modalita_terminale():
    print("=" * 50)
    print("  🔗 Crea Scorciatoia Web per Ubuntu (Firefox)")
    print("=" * 50)
    print(f"  Firefox trovato: {FIREFOX}")
    print(f"  Cartella icone:  {ICONS_PATH}")
    print()

    while True:
        nome = input("📌 Nome scorciatoia (es. YouTube): ").strip()
        if not nome:
            print("⚠️  Il nome non può essere vuoto.")
            continue

        url = input("🌐 URL (es. https://youtube.com): ").strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        print(f"🖼️  Icona da {ICONS_PATH}")
        icona = input("   Nome file icona (es. youtube.png) o invio per saltare: ").strip()

        crea_file_desktop(nome, url, icona)

        altro = input("\n➕ Aggiungere un'altra? (s/n): ").strip().lower()
        if altro != "s":
            break

    print(f"\n🎉 Fatto! Controlla il Desktop: {DESKTOP_PATH}")
    print("💡 Se vedi un lucchetto → clic destro sull'icona → 'Consenti avvio'")


def modalita_gui():
    try:
        import tkinter as tk
        from tkinter import messagebox
    except ImportError:
        print("⚠️  tkinter non disponibile. Avvio modalità terminale...")
        modalita_terminale()
        return

    root = tk.Tk()
    root.title("Crea Scorciatoia Web")
    root.geometry("460x390")
    root.resizable(False, False)
    root.configure(bg="#1e1e2e")

    BG = "#1e1e2e"
    CARD = "#2a2a3e"
    ACCENT = "#7c3aed"
    FG = "#e2e8f0"
    MUTED = "#94a3b8"
    ENTRY_BG = "#313149"
    GREEN = "#4ade80"

    tk.Label(root, text="🔗 Crea Scorciatoia Web", font=("monospace", 15, "bold"),
             bg=BG, fg=ACCENT).pack(pady=(18, 2))
    tk.Label(root, text=f"Firefox: {FIREFOX}", font=("monospace", 8),
             bg=BG, fg=MUTED).pack()

    frame = tk.Frame(root, bg=CARD, padx=24, pady=20)
    frame.pack(padx=20, pady=12, fill="x")

    def lbl(t):
        tk.Label(frame, text=t, font=("monospace", 8, "bold"),
                 bg=CARD, fg=MUTED, anchor="w").pack(fill="x", pady=(8, 2))

    def ent(placeholder=""):
        e = tk.Entry(frame, font=("monospace", 11), bg=ENTRY_BG, fg=FG,
                     insertbackground=FG, relief="flat", bd=6)
        e.pack(fill="x", ipady=4)
        if placeholder:
            e.insert(0, placeholder)
            e.config(fg=MUTED)
            def on_focus_in(ev):
                if e.get() == placeholder:
                    e.delete(0, tk.END)
                    e.config(fg=FG)
            def on_focus_out(ev):
                if not e.get():
                    e.insert(0, placeholder)
                    e.config(fg=MUTED)
            e.bind("<FocusIn>", on_focus_in)
            e.bind("<FocusOut>", on_focus_out)
        return e

    lbl("NOME SCORCIATOIA")
    e_nome = ent("es. YouTube")

    lbl("URL DEL SITO")
    e_url = ent("https://")

    lbl(f"ICONA — solo nome file da {ICONS_PATH}")
    e_icona = ent("es. youtube.png  (lascia vuoto per default)")

    stato_var = tk.StringVar()
    tk.Label(root, textvariable=stato_var, font=("monospace", 9),
             bg=BG, fg=GREEN, wraplength=420).pack(pady=4)

    def on_crea():
        nome = e_nome.get().strip()
        url = e_url.get().strip()
        icona_raw = e_icona.get().strip()
        # Ignora il placeholder
        if "lascia vuoto" in icona_raw or icona_raw == "es. youtube.png  (lascia vuoto per default)":
            icona_raw = ""

        if not nome or nome == "es. YouTube":
            messagebox.showwarning("Attenzione", "Inserisci il nome della scorciatoia.")
            return
        if url in ("https://", ""):
            messagebox.showwarning("Attenzione", "Inserisci un URL valido.")
            return
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        crea_file_desktop(nome, url, icona_raw, gui=True, parent=root)
        stato_var.set(f"✅ '{nome}' creata sul Desktop!")

        e_nome.delete(0, tk.END)
        e_nome.insert(0, "es. YouTube")
        e_nome.config(fg=MUTED)
        e_url.delete(0, tk.END)
        e_url.insert(0, "https://")
        e_url.config(fg=MUTED)
        e_icona.delete(0, tk.END)
        e_icona.insert(0, "es. youtube.png  (lascia vuoto per default)")
        e_icona.config(fg=MUTED)

    tk.Button(root, text="✚  CREA SCORCIATOIA",
              font=("monospace", 11, "bold"),
              bg=ACCENT, fg="white",
              activebackground="#6d28d9", activeforeground="white",
              relief="flat", bd=0, padx=20, pady=10,
              cursor="hand2", command=on_crea).pack(pady=(0, 16))

    root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        icona_arg = sys.argv[3] if len(sys.argv) >= 4 else ""
        crea_file_desktop(sys.argv[1], sys.argv[2], icona_arg)
        sys.exit(0)

    if "--terminale" in sys.argv:
        modalita_terminale()
    else:
        try:
            import tkinter
            modalita_gui()
        except ImportError:
            modalita_terminale()
