#!/usr/bin/env python3
"""
Arc Studio → IONOS Upload
Einfach im Terminal ausführen:  python3 upload-to-ionos.py
Kein extra Tool nötig — nutzt Python's eingebautes ftplib
"""

import ftplib, os, sys, ssl
from pathlib import Path

# ── ZUGANGSDATEN ──────────────────────────────────────────────
HOST = "access-5020436626.webspace-host.com"
USER = "su167909"
PASS = "gunnar-huvqa3-byHguj"
REMOTE_ROOT = "/"

# ── DATEIEN ZUM HOCHLADEN ─────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent

FILES = [
    "index.html",
    "voltiq.html",
    "VOLTECH-ampere.html",
    "VOLTECH-torque.html",
    "VOLTECH-ki.html",
    "VOLTECH-lern-basis.html",
    "VOLTECH-lern-extra.html",
    "VOLTECH-mechatronik-pro.html",
    "VOLTECH-sps.html",
    "VOLTECH-berichtsheft.html",
    "VOLTECH-tools2.html",
    "impressum.html",
    "datenschutz.html",
    ".htaccess",
    "pwa/manifest.json",
    "pwa/sw.js",
]

# ── FARBEN ────────────────────────────────────────────────────
GRN = "\033[92m"; RED = "\033[91m"; YLW = "\033[93m"; RST = "\033[0m"; BLD = "\033[1m"

def upload():
    print(f"\n{BLD}══════════════════════════════════════════{RST}")
    print(f"{BLD}  Arc Studio → IONOS Upload{RST}")
    print(f"{BLD}══════════════════════════════════════════{RST}\n")
    print(f"{YLW}📡 Verbinde zu {HOST}...{RST}")

    ftp = None
    try:
        # Versuche erst FTPS (sicherer), dann plain FTP
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            ftp = ftplib.FTP_TLS(timeout=30)
            ftp.connect(HOST, 21)
            ftp.auth()
            ftp.login(USER, PASS)
            ftp.prot_p()
            print(f"{GRN}✅ Verbunden (FTPS){RST}\n")
        except Exception:
            ftp = ftplib.FTP(timeout=30)
            ftp.connect(HOST, 21)
            ftp.login(USER, PASS)
            print(f"{GRN}✅ Verbunden (FTP){RST}\n")

        ftp.set_pasv(True)

        # /pwa/ Verzeichnis sicherstellen
        try:
            ftp.mkd("/pwa")
        except ftplib.error_perm:
            pass  # Existiert bereits

        ok = 0
        fail = 0

        for rel_path in FILES:
            local_file = SCRIPT_DIR / rel_path
            remote_path = REMOTE_ROOT.rstrip("/") + "/" + rel_path

            if not local_file.exists():
                print(f"  {YLW}⚠ Übersprungen (nicht gefunden): {rel_path}{RST}")
                continue

            try:
                with open(local_file, "rb") as f:
                    ftp.storbinary(f"STOR {remote_path}", f)
                size_kb = local_file.stat().st_size / 1024
                print(f"  {GRN}✅ {rel_path:<45}{RST} {size_kb:>6.1f} KB")
                ok += 1
            except Exception as e:
                print(f"  {RED}❌ {rel_path}: {e}{RST}")
                fail += 1

        ftp.quit()

        print(f"\n{BLD}══════════════════════════════════════════{RST}")
        if fail == 0:
            print(f"{GRN}{BLD}  ✅ Upload abgeschlossen! {ok} Dateien hochgeladen.{RST}")
            print(f"{BLD}══════════════════════════════════════════{RST}")
            print(f"\n  🌐 Webseite:  https://arc-studio.org")
            print(f"  📋 Nächster Schritt: SSL in IONOS Control Panel aktivieren\n")
        else:
            print(f"{YLW}{BLD}  ⚠ {ok} OK · {fail} Fehler — prüfe Ausgabe oben{RST}")
            print(f"{BLD}══════════════════════════════════════════{RST}\n")

    except ConnectionRefusedError:
        print(f"\n{RED}❌ Verbindung verweigert — prüfe Host/Port{RST}")
        sys.exit(1)
    except TimeoutError:
        print(f"\n{RED}❌ Timeout — prüfe Netzwerk/Firewall{RST}")
        sys.exit(1)
    except ftplib.error_perm as e:
        print(f"\n{RED}❌ Login fehlgeschlagen: {e}{RST}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}❌ Fehler: {e}{RST}")
        if ftp:
            try: ftp.quit()
            except: pass
        sys.exit(1)

if __name__ == "__main__":
    upload()
