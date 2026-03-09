/*
 * scorcy_win.cpp
 * Crea scorciatoie web sul Desktop di Windows.
 * Supporta selezione browser: predefinito o specifico (Chrome, Firefox, Edge, ecc.)
 * Scorciatoie con browser specifico vengono create come file .lnk (via PowerShell WScript.Shell).
 *
 * Modalita:
 *   scorcy_win.exe                                          -> GUI
 *   scorcy_win.exe --terminale                              -> terminale interattivo
 *   scorcy_win.exe "YouTube" "https://..."                  -> inline, browser predefinito
 *   scorcy_win.exe "YouTube" "https://..." "icona.ico"      -> inline con icona
 *   scorcy_win.exe "YouTube" "https://..." "" "chrome"      -> inline con browser
 *   scorcy_win.exe "YouTube" "https://..." "y.ico" "chrome" -> inline completo
 *
 * Compilazione (MinGW):
 *   g++ scorcy_win.cpp -o scorcy_win.exe -mwindows -municode
 */

#ifndef UNICODE
#define UNICODE
#endif
#ifndef _UNICODE
#define _UNICODE
#endif

#include <windows.h>
#include <shlobj.h>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>

// ─── Costanti ────────────────────────────────────────────────────────────────

const std::wstring ICONS_SUBDIR = L"Icons";

#define ID_BTN_CREA    101
#define ID_EDIT_NOME   102
#define ID_EDIT_URL    103
#define ID_EDIT_ICON   104
#define ID_LABEL_OK    105
#define ID_COMBO_BROWSER 106

// ─── Struttura browser ───────────────────────────────────────────────────────

struct Browser {
    std::wstring nome;
    std::wstring exe;   // percorso completo
};

// ─── Rilevamento browser installati ─────────────────────────────────────────

std::vector<Browser> rileva_browser() {
    std::vector<Browser> lista;

    // Percorsi candidati per ogni browser
    struct Candidato {
        std::wstring nome;
        std::vector<std::wstring> percorsi;
    };

    wchar_t pf[MAX_PATH], pf86[MAX_PATH], local[MAX_PATH];
    SHGetFolderPathW(NULL, CSIDL_PROGRAM_FILES,       NULL, 0, pf);
    SHGetFolderPathW(NULL, CSIDL_PROGRAM_FILESX86,    NULL, 0, pf86);
    SHGetFolderPathW(NULL, CSIDL_LOCAL_APPDATA,       NULL, 0, local);

    std::wstring PF    = pf;
    std::wstring PF86  = pf86;
    std::wstring LOCAL = local;

    std::vector<Candidato> candidati = {
        { L"Google Chrome", {
            PF    + L"\\Google\\Chrome\\Application\\chrome.exe",
            PF86  + L"\\Google\\Chrome\\Application\\chrome.exe",
            LOCAL + L"\\Google\\Chrome\\Application\\chrome.exe"
        }},
        { L"Mozilla Firefox", {
            PF    + L"\\Mozilla Firefox\\firefox.exe",
            PF86  + L"\\Mozilla Firefox\\firefox.exe"
        }},
        { L"Microsoft Edge", {
            PF    + L"\\Microsoft\\Edge\\Application\\msedge.exe",
            PF86  + L"\\Microsoft\\Edge\\Application\\msedge.exe"
        }},
        { L"Brave", {
            PF    + L"\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
            PF86  + L"\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
            LOCAL + L"\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
        }},
        { L"Opera", {
            PF    + L"\\Opera\\launcher.exe",
            LOCAL + L"\\Programs\\Opera\\launcher.exe"
        }},
        { L"Vivaldi", {
            PF    + L"\\Vivaldi\\Application\\vivaldi.exe",
            LOCAL + L"\\Vivaldi\\Application\\vivaldi.exe"
        }},
    };

    for (const auto& c : candidati) {
        for (const auto& p : c.percorsi) {
            if (GetFileAttributesW(p.c_str()) != INVALID_FILE_ATTRIBUTES) {
                lista.push_back({ c.nome, p });
                break;
            }
        }
    }

    return lista;
}

// ─── Utilita percorsi ─────────────────────────────────────────────────────────

std::wstring get_desktop_path() {
    wchar_t path[MAX_PATH];
    SHGetFolderPathW(NULL, CSIDL_DESKTOPDIRECTORY, NULL, 0, path);
    return std::wstring(path);
}

std::wstring get_icons_path() {
    wchar_t profile[MAX_PATH];
    GetEnvironmentVariableW(L"USERPROFILE", profile, MAX_PATH);
    return std::wstring(profile) + L"\\" + ICONS_SUBDIR;
}

void assicura_cartella_icons() {
    std::wstring path = get_icons_path();
    if (GetFileAttributesW(path.c_str()) == INVALID_FILE_ATTRIBUTES)
        CreateDirectoryW(path.c_str(), NULL);
}

// ─── Pulizia nome file ────────────────────────────────────────────────────────

std::wstring pulisci_nome(const std::wstring& nome) {
    std::wstring result;
    const std::wstring vietati = L"\\/:*?\"<>|";
    for (wchar_t c : nome) {
        if (vietati.find(c) == std::wstring::npos)
            result += c;
    }
    size_t start = result.find_first_not_of(L" \t");
    size_t end   = result.find_last_not_of(L" \t");
    if (start == std::wstring::npos) return L"";
    return result.substr(start, end - start + 1);
}

// ─── Risoluzione icona ────────────────────────────────────────────────────────

std::wstring risolvi_icona(const std::wstring& nome_icona) {
    if (nome_icona.empty()) return L"";
    std::wstring icons_path = get_icons_path();
    std::wstring percorso   = icons_path + L"\\" + nome_icona;
    if (GetFileAttributesW(percorso.c_str()) != INVALID_FILE_ATTRIBUTES)
        return percorso;
    for (const auto& ext : std::vector<std::wstring>{ L".ico", L".png", L".jpg", L".bmp" }) {
        std::wstring t = percorso + ext;
        if (GetFileAttributesW(t.c_str()) != INVALID_FILE_ATTRIBUTES)
            return t;
    }
    return L"";
}

// ─── Controllo nomi duplicati ────────────────────────────────────────────────

bool chiedi_sovrascrittura(const std::wstring& percorso_file,
                           const std::wstring& nome_file,
                           const std::string& modalita,
                           HWND hwnd_parent = NULL)
{
    if (GetFileAttributesW(percorso_file.c_str()) == INVALID_FILE_ATTRIBUTES)
        return true;  // non esiste, si puo procedere

    if (modalita == "gui") {
        std::wstring msg = L"Esiste gia una scorciatoia '" + nome_file + L"'.\nSovrascrivere?";
        int ris = MessageBoxW(hwnd_parent, msg.c_str(), L"File esistente", MB_YESNO | MB_ICONQUESTION);
        return ris == IDYES;
    }

    // Terminale e inline: chiedi su console
    std::wcout << L"\n Attenzione: esiste gia '" << nome_file << L"'. Sovrascrivere? (s/n): ";
    std::wstring ris;
    std::getline(std::wcin, ris);
    return ris == L"s" || ris == L"S";
}

// ─── Creazione .url (browser predefinito) ────────────────────────────────────

bool crea_url(const std::wstring& desktop,
              const std::wstring& nome_ok,
              const std::wstring& url,
              const std::wstring& icon_path,
              const std::string& modalita = "inline",
              HWND hwnd_parent = NULL)
{
    std::wstring percorso_file = desktop + L"\\" + nome_ok + L".url";
    if (!chiedi_sovrascrittura(percorso_file, nome_ok + L".url", modalita, hwnd_parent))
        return false;
    std::wofstream file(percorso_file.c_str());
    if (!file.is_open()) return false;

    file << L"[InternetShortcut]\n";
    file << L"URL=" << url << L"\n";
    if (!icon_path.empty()) {
        file << L"IconFile=" << icon_path << L"\n";
        file << L"IconIndex=0\n";
    }
    file.close();
    std::wcout << L"     File:  " << percorso_file << L"\n";
    return true;
}

// ─── Creazione .lnk (browser specifico via PowerShell) ───────────────────────

bool crea_lnk(const std::wstring& desktop,
              const std::wstring& nome_ok,
              const std::wstring& url,
              const std::wstring& browser_exe,
              const std::wstring& icon_path,
              const std::string& modalita = "inline",
              HWND hwnd_parent = NULL)
{
    std::wstring percorso_file = desktop + L"\\" + nome_ok + L".lnk";
    if (!chiedi_sovrascrittura(percorso_file, nome_ok + L".lnk", modalita, hwnd_parent))
        return false;

    // Usa PowerShell per creare il .lnk in modo affidabile
    // Escape delle virgolette per PowerShell
    auto ps_escape = [](std::wstring s) -> std::wstring {
        std::wstring r;
        for (wchar_t c : s) {
            if (c == L'\'') r += L"''";
            else r += c;
        }
        return r;
    };

    std::wstring lnk_path_esc    = ps_escape(percorso_file);
    std::wstring browser_exe_esc = ps_escape(browser_exe);
    std::wstring url_esc         = ps_escape(url);
    std::wstring icon_esc        = icon_path.empty() ? ps_escape(browser_exe) : ps_escape(icon_path);

    // Costruisci script PowerShell inline
    std::wstring ps =
        L"$s=(New-Object -COM WScript.Shell).CreateShortcut('" + lnk_path_esc + L"');"
        L"$s.TargetPath='" + browser_exe_esc + L"';"
        L"$s.Arguments='" + url_esc + L"';"
        L"$s.IconLocation='" + icon_esc + L",0';"
        L"$s.Save()";

    // Esegui PowerShell nascosto
    std::wstring cmd = L"powershell.exe -NoProfile -NonInteractive -WindowStyle Hidden -Command "" + ps + L""";

    STARTUPINFOW si = {};
    si.cb = sizeof(si);
    si.dwFlags = STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_HIDE;
    PROCESS_INFORMATION pi = {};

    std::vector<wchar_t> cmd_buf(cmd.begin(), cmd.end());
    cmd_buf.push_back(L'\0');

    BOOL ok = CreateProcessW(NULL, cmd_buf.data(), NULL, NULL, FALSE,
                             CREATE_NO_WINDOW, NULL, NULL, &si, &pi);
    if (!ok) return false;

    // Attendi il completamento (max 5 secondi)
    WaitForSingleObject(pi.hProcess, 5000);

    DWORD exit_code = 1;
    GetExitCodeProcess(pi.hProcess, &exit_code);
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);

    if (exit_code == 0 && GetFileAttributesW(percorso_file.c_str()) != INVALID_FILE_ATTRIBUTES) {
        std::wcout << L"     File:  " << percorso_file << L"\n";
        return true;
    }
    return false;
}

// ─── Funzione principale di creazione ────────────────────────────────────────

bool crea_scorciatoia(const std::wstring& nome,
                      const std::wstring& url,
                      const std::wstring& nome_icona,
                      const std::wstring& browser_exe,  // vuoto = predefinito
                      const std::string& modalita = "inline",
                      HWND hwnd_parent = NULL)
{
    std::wstring desktop  = get_desktop_path();
    std::wstring nome_ok  = pulisci_nome(nome);
    if (nome_ok.empty()) {
        std::wcout << L"Errore: nome non valido.\n";
        return false;
    }

    std::wstring icon_path = risolvi_icona(nome_icona);

    std::wcout << L"\n OK  Scorciatoia creata!\n";
    std::wcout << L"     URL:   " << url << L"\n";

    bool ok;
    if (browser_exe.empty()) {
        ok = crea_url(desktop, nome_ok, url, icon_path, modalita, hwnd_parent);
        std::wcout << L"     Browser: (predefinito)\n";
    } else {
        ok = crea_lnk(desktop, nome_ok, url, browser_exe, icon_path, modalita, hwnd_parent);
        std::wcout << L"     Browser: " << browser_exe << L"\n";
    }

    if (!ok) {
        // false puo significare annullato dall'utente oppure errore I/O
        return false;
    }

    std::wcout << (icon_path.empty()
        ? L"     Icona:  (predefinita del browser)\n"
        : L"     Icona:  " + icon_path + L"\n");

    return true;
}

// ─── MODALITA TERMINALE ───────────────────────────────────────────────────────

void modalita_terminale() {
    assicura_cartella_icons();
    AllocConsole();
    FILE* f;
    freopen_s(&f, "CONOUT$", "w", stdout);
    freopen_s(&f, "CONIN$",  "r", stdin);

    std::wstring icons_path = get_icons_path();
    std::wstring desktop    = get_desktop_path();
    auto browser_list       = rileva_browser();

    std::wcout << L"================================================\n";
    std::wcout << L"   Scorcy -- Crea Scorciatoia Web per Windows\n";
    std::wcout << L"================================================\n";
    std::wcout << L"  Desktop:        " << desktop    << L"\n";
    std::wcout << L"  Cartella icone: " << icons_path << L"\n\n";

    while (true) {
        std::wstring nome, url, icona, browser_exe;

        std::wcout << L"Nome scorciatoia (es. YouTube): ";
        std::getline(std::wcin, nome);
        if (nome.empty()) { std::wcout << L"  Il nome non puo essere vuoto.\n"; continue; }

        std::wcout << L"URL del sito (es. https://youtube.com): ";
        std::getline(std::wcin, url);
        if (url.find(L"http") != 0) url = L"https://" + url;

        std::wcout << L"Icona da " << icons_path << L"\n";
        std::wcout << L"  Nome file (es. youtube.ico) o invio per saltare: ";
        std::getline(std::wcin, icona);

        // Selezione browser
        std::wcout << L"\nBrowser disponibili:\n";
        std::wcout << L"  0. Browser predefinito\n";
        for (size_t i = 0; i < browser_list.size(); i++)
            std::wcout << L"  " << (i+1) << L". " << browser_list[i].nome << L"\n";
        std::wcout << L"Scelta (invio per predefinito): ";
        std::wstring scelta_str;
        std::getline(std::wcin, scelta_str);

        if (!scelta_str.empty()) {
            int scelta = _wtoi(scelta_str.c_str());
            if (scelta >= 1 && scelta <= (int)browser_list.size())
                browser_exe = browser_list[scelta - 1].exe;
        }

        crea_scorciatoia(nome, url, icona, browser_exe, "terminale");

        std::wstring altro;
        std::wcout << L"\nAggiungere un'altra? (s/n): ";
        std::getline(std::wcin, altro);
        if (altro != L"s" && altro != L"S") break;
    }

    std::wcout << L"\nFatto! Controlla il Desktop.\n";
    std::wcout << L"Premi INVIO per chiudere...";
    std::wstring dummy;
    std::getline(std::wcin, dummy);
}

// ─── MODALITA INLINE ─────────────────────────────────────────────────────────

void modalita_inline(const std::wstring& nome,
                     const std::wstring& url,
                     const std::wstring& icona,
                     const std::wstring& browser_hint)  // nome parziale es. "chrome"
{
    assicura_cartella_icons();
    AllocConsole();
    FILE* f;
    freopen_s(&f, "CONOUT$", "w", stdout);

    // Cerca il browser per nome parziale
    std::wstring browser_exe;
    if (!browser_hint.empty()) {
        auto lista = rileva_browser();
        std::wstring hint_lower = browser_hint;
        for (auto& c : hint_lower) c = towlower(c);
        for (const auto& b : lista) {
            std::wstring nome_lower = b.nome;
            for (auto& c : nome_lower) c = towlower(c);
            if (nome_lower.find(hint_lower) != std::wstring::npos) {
                browser_exe = b.exe;
                break;
            }
        }
        if (browser_exe.empty())
            std::wcout << L"Avviso: browser '" << browser_hint << L"' non trovato, uso predefinito.\n";
    }

    crea_scorciatoia(nome, url, icona, browser_exe, "inline");

    std::wcout << L"\nPremi INVIO per chiudere...";
    freopen_s(&f, "CONIN$", "r", stdin);
    std::wstring dummy;
    std::getline(std::wcin, dummy);
}

// ─── GUI ──────────────────────────────────────────────────────────────────────

#define COL_BG     RGB( 30,  30,  46)
#define COL_ACCENT RGB(124,  58, 237)
#define COL_FG     RGB(226, 232, 240)
#define COL_MUTED  RGB(148, 163, 184)
#define COL_GREEN  RGB( 74, 222, 128)
#define COL_ENTRY  RGB( 49,  49,  73)

HFONT  hFontTitle, hFontLabel, hFontEntry, hFontBtn;
HBRUSH hBrushBg, hBrushEntry;

HWND hEditNome, hEditUrl, hEditIcon, hComboBrowser, hLabelOk;

std::vector<Browser> g_browser_list;

std::wstring get_edit_text(HWND hwnd) {
    int len = GetWindowTextLengthW(hwnd);
    if (len == 0) return L"";
    std::wstring buf(len + 1, L'\0');
    GetWindowTextW(hwnd, &buf[0], len + 1);
    buf.resize(len);
    return buf;
}

void on_crea_click(HWND hwnd) {
    std::wstring nome  = get_edit_text(hEditNome);
    std::wstring url   = get_edit_text(hEditUrl);
    std::wstring icona = get_edit_text(hEditIcon);

    if (nome.empty()) {
        MessageBoxW(hwnd, L"Inserisci il nome della scorciatoia.", L"Attenzione", MB_ICONWARNING);
        return;
    }
    if (url.empty() || url == L"https://") {
        MessageBoxW(hwnd, L"Inserisci un URL valido.", L"Attenzione", MB_ICONWARNING);
        return;
    }
    if (url.find(L"http") != 0) url = L"https://" + url;

    // Leggi selezione browser dalla ComboBox
    std::wstring browser_exe;
    int sel = (int)SendMessageW(hComboBrowser, CB_GETCURSEL, 0, 0);
    // 0 = predefinito, 1..N = browser trovati
    if (sel >= 1 && sel <= (int)g_browser_list.size())
        browser_exe = g_browser_list[sel - 1].exe;

    if (crea_scorciatoia(nome, url, icona, browser_exe, "gui", hwnd)) {
        std::wstring msg = L"'" + nome + L"' creata sul Desktop!";
        SetWindowTextW(hLabelOk, msg.c_str());
        SetWindowTextW(hEditNome, L"");
        SetWindowTextW(hEditUrl,  L"https://");
        SetWindowTextW(hEditIcon, L"");
        SendMessageW(hComboBrowser, CB_SETCURSEL, 0, 0);
    }
}

LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wp, LPARAM lp) {
    switch (msg) {

    case WM_CREATE: {
        hFontTitle = CreateFontW(22, 0, 0, 0, FW_BOLD,   0, 0, 0, DEFAULT_CHARSET, 0, 0, CLEARTYPE_QUALITY, 0, L"Consolas");
        hFontLabel = CreateFontW(14, 0, 0, 0, FW_BOLD,   0, 0, 0, DEFAULT_CHARSET, 0, 0, CLEARTYPE_QUALITY, 0, L"Consolas");
        hFontEntry = CreateFontW(16, 0, 0, 0, FW_NORMAL, 0, 0, 0, DEFAULT_CHARSET, 0, 0, CLEARTYPE_QUALITY, 0, L"Consolas");
        hFontBtn   = CreateFontW(16, 0, 0, 0, FW_BOLD,   0, 0, 0, DEFAULT_CHARSET, 0, 0, CLEARTYPE_QUALITY, 0, L"Consolas");
        hBrushBg    = CreateSolidBrush(COL_BG);
        hBrushEntry = CreateSolidBrush(COL_ENTRY);

        int W = 480;

        // Titolo
        HWND hT = CreateWindowW(L"STATIC", L"Scorcy  \x2014  Crea Scorciatoia Web",
            WS_CHILD|WS_VISIBLE|SS_CENTER, 0, 18, W, 28, hwnd, NULL, NULL, NULL);
        SendMessageW(hT, WM_SETFONT, (WPARAM)hFontTitle, TRUE);

        HWND hS = CreateWindowW(L"STATIC", L"Windows  |  Scegli il browser",
            WS_CHILD|WS_VISIBLE|SS_CENTER, 0, 50, W, 18, hwnd, NULL, NULL, NULL);
        SendMessageW(hS, WM_SETFONT, (WPARAM)hFontLabel, TRUE);

        // NOME
        HWND lN = CreateWindowW(L"STATIC", L"NOME SCORCIATOIA",
            WS_CHILD|WS_VISIBLE, 40, 82, W-80, 18, hwnd, NULL, NULL, NULL);
        SendMessageW(lN, WM_SETFONT, (WPARAM)hFontLabel, TRUE);
        hEditNome = CreateWindowExW(WS_EX_CLIENTEDGE, L"EDIT", L"",
            WS_CHILD|WS_VISIBLE|ES_AUTOHSCROLL, 40, 102, W-80, 28, hwnd, (HMENU)ID_EDIT_NOME, NULL, NULL);
        SendMessageW(hEditNome, WM_SETFONT, (WPARAM)hFontEntry, TRUE);

        // URL
        HWND lU = CreateWindowW(L"STATIC", L"URL DEL SITO",
            WS_CHILD|WS_VISIBLE, 40, 140, W-80, 18, hwnd, NULL, NULL, NULL);
        SendMessageW(lU, WM_SETFONT, (WPARAM)hFontLabel, TRUE);
        hEditUrl = CreateWindowExW(WS_EX_CLIENTEDGE, L"EDIT", L"https://",
            WS_CHILD|WS_VISIBLE|ES_AUTOHSCROLL, 40, 160, W-80, 28, hwnd, (HMENU)ID_EDIT_URL, NULL, NULL);
        SendMessageW(hEditUrl, WM_SETFONT, (WPARAM)hFontEntry, TRUE);

        // ICONA
        HWND lI = CreateWindowW(L"STATIC", L"ICONA  (nome file da %USERPROFILE%\\Icons)",
            WS_CHILD|WS_VISIBLE, 40, 198, W-80, 18, hwnd, NULL, NULL, NULL);
        SendMessageW(lI, WM_SETFONT, (WPARAM)hFontLabel, TRUE);
        hEditIcon = CreateWindowExW(WS_EX_CLIENTEDGE, L"EDIT", L"",
            WS_CHILD|WS_VISIBLE|ES_AUTOHSCROLL, 40, 218, W-80, 28, hwnd, (HMENU)ID_EDIT_ICON, NULL, NULL);
        SendMessageW(hEditIcon, WM_SETFONT, (WPARAM)hFontEntry, TRUE);

        // BROWSER
        HWND lB = CreateWindowW(L"STATIC", L"BROWSER",
            WS_CHILD|WS_VISIBLE, 40, 256, W-80, 18, hwnd, NULL, NULL, NULL);
        SendMessageW(lB, WM_SETFONT, (WPARAM)hFontLabel, TRUE);
        hComboBrowser = CreateWindowW(L"COMBOBOX", L"",
            WS_CHILD|WS_VISIBLE|CBS_DROPDOWNLIST|WS_VSCROLL,
            40, 276, W-80, 160, hwnd, (HMENU)ID_COMBO_BROWSER, NULL, NULL);
        SendMessageW(hComboBrowser, WM_SETFONT, (WPARAM)hFontEntry, TRUE);

        // Popola ComboBox
        SendMessageW(hComboBrowser, CB_ADDSTRING, 0, (LPARAM)L"Browser predefinito");
        for (const auto& b : g_browser_list)
            SendMessageW(hComboBrowser, CB_ADDSTRING, 0, (LPARAM)b.nome.c_str());
        SendMessageW(hComboBrowser, CB_SETCURSEL, 0, 0);

        // Label OK
        hLabelOk = CreateWindowW(L"STATIC", L"",
            WS_CHILD|WS_VISIBLE|SS_CENTER, 0, 316, W, 20, hwnd, (HMENU)ID_LABEL_OK, NULL, NULL);
        SendMessageW(hLabelOk, WM_SETFONT, (WPARAM)hFontLabel, TRUE);

        // Bottone
        HWND hBtn = CreateWindowW(L"BUTTON", L"CREA SCORCIATOIA",
            WS_CHILD|WS_VISIBLE|BS_PUSHBUTTON, 120, 344, W-240, 36,
            hwnd, (HMENU)ID_BTN_CREA, NULL, NULL);
        SendMessageW(hBtn, WM_SETFONT, (WPARAM)hFontBtn, TRUE);

        return 0;
    }

    case WM_COMMAND:
        if (LOWORD(wp) == ID_BTN_CREA) on_crea_click(hwnd);
        return 0;

    case WM_CTLCOLORSTATIC: {
        HDC hdc = (HDC)wp; HWND hCtrl = (HWND)lp;
        SetBkMode(hdc, TRANSPARENT);
        SetTextColor(hdc, hCtrl == hLabelOk ? COL_GREEN : COL_MUTED);
        return (LRESULT)hBrushBg;
    }
    case WM_CTLCOLOREDIT: {
        HDC hdc = (HDC)wp;
        SetBkColor(hdc, COL_ENTRY);
        SetTextColor(hdc, COL_FG);
        return (LRESULT)hBrushEntry;
    }
    case WM_ERASEBKGND: {
        RECT rc; GetClientRect(hwnd, &rc);
        FillRect((HDC)wp, &rc, hBrushBg);
        return 1;
    }
    case WM_DESTROY:
        DeleteObject(hFontTitle); DeleteObject(hFontLabel);
        DeleteObject(hFontEntry); DeleteObject(hFontBtn);
        DeleteObject(hBrushBg);   DeleteObject(hBrushEntry);
        PostQuitMessage(0);
        return 0;
    }
    return DefWindowProcW(hwnd, msg, wp, lp);
}

void modalita_gui(HINSTANCE hInst) {
    assicura_cartella_icons();
    g_browser_list = rileva_browser();

    WNDCLASSW wc   = {};
    wc.lpfnWndProc = WndProc;
    wc.hInstance   = hInst;
    wc.lpszClassName = L"ScorcyWin";
    wc.hbrBackground = CreateSolidBrush(COL_BG);
    wc.hCursor       = LoadCursor(NULL, IDC_ARROW);
    RegisterClassW(&wc);

    HWND hwnd = CreateWindowExW(0, L"ScorcyWin",
        L"Scorcy \x2014 Crea Scorciatoia Web",
        WS_OVERLAPPED|WS_CAPTION|WS_SYSMENU|WS_MINIMIZEBOX,
        CW_USEDEFAULT, CW_USEDEFAULT, 480, 420,
        NULL, NULL, hInst, NULL);

    ShowWindow(hwnd, SW_SHOW);
    UpdateWindow(hwnd);

    MSG msg;
    while (GetMessageW(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }
}

// ─── ENTRY POINT ─────────────────────────────────────────────────────────────

int WINAPI wWinMain(HINSTANCE hInst, HINSTANCE, LPWSTR, int) {
    int argc;
    LPWSTR* argv = CommandLineToArgvW(GetCommandLineW(), &argc);

    if (argc >= 3) {
        std::wstring nome         = argv[1];
        std::wstring url          = argv[2];
        std::wstring icona        = (argc >= 4) ? argv[3] : L"";
        std::wstring browser_hint = (argc >= 5) ? argv[4] : L"";
        LocalFree(argv);
        modalita_inline(nome, url, icona, browser_hint);
        return 0;
    }

    if (argc >= 2 && std::wstring(argv[1]) == L"--terminale") {
        LocalFree(argv);
        modalita_terminale();
        return 0;
    }

    LocalFree(argv);
    modalita_gui(hInst);
    return 0;
}
