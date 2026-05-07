# ea_batch_export_gui.py
# Voraussetzung:
#   Windows
#   Sparx Enterprise Architect installiert und COM registriert
#   export_all_diagrams.js liegt im gleichen Ordner wie diese Python-Datei

import csv
import re
import sqlite3
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

EA_EXTENSIONS = {".qea", ".qeax", ".eap", ".eapx", ".feap"}
QEA_EXTENSIONS = {".qea"}


def _sanitize_filename(name: str) -> str:
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    s = re.sub(r'\s+', " ", s).strip().rstrip(".")
    return s[:120] or "EA_Model"


def _unique_model_folder(output_dir: Path, stem: str) -> Path:
    base = _sanitize_filename(stem)
    candidate = output_dir / base
    i = 2
    while candidate.exists():
        candidate = output_dir / f"{base}_{i}"
        i += 1
    return candidate


def export_names_txt(qea_file: Path, output_dir: Path, log_fn) -> None:
    out_file = output_dir / "names.txt"
    try:
        con = sqlite3.connect(f"file:{qea_file}?mode=ro", uri=True)
        try:
            cur = con.execute(
                "SELECT Name, ea_guid, Stereotype, Note, DATE(ModifiedDate) FROM t_object ORDER BY Name"
            )
            with open(out_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_MINIMAL)
                writer.writerow(["Name", "ea_guid", "Stereotype", "Notes", "Datum"])
                for row in cur:
                    writer.writerow([v if v is not None else "" for v in row])
            log_fn(f"  names.txt erstellt: {out_file}\n")
        finally:
            con.close()
    except Exception as exc:
        log_fn(f"  WARNUNG: names.txt konnte nicht erstellt werden: {exc}\n")


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Sparx EA Diagramm Batch Export")
        self.geometry("850x520")

        self.search_dir = tk.StringVar()
        self.output_dir = tk.StringVar()

        self.create_ui()

    def create_ui(self):
        frame = tk.Frame(self)
        frame.pack(fill="x", padx=10, pady=10)

        tk.Label(frame, text="Ordner durchsuchen:").grid(row=0, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.search_dir, width=90).grid(row=0, column=1, padx=5)
        tk.Button(frame, text="Auswählen", command=self.pick_search_dir).grid(row=0, column=2)

        tk.Label(frame, text="Ergebnisordner:").grid(row=1, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.output_dir, width=90).grid(row=1, column=1, padx=5)
        tk.Button(frame, text="Auswählen", command=self.pick_output_dir).grid(row=1, column=2)

        self.start_button = tk.Button(self, text="Export starten", command=self.start_export)
        self.start_button.pack(pady=5)

        self.log = tk.Text(self, wrap="word")
        self.log.pack(fill="both", expand=True, padx=10, pady=10)

    def pick_search_dir(self):
        folder = filedialog.askdirectory(title="Ordner zur Durchsuchung auswählen")
        if folder:
            self.search_dir.set(folder)

    def pick_output_dir(self):
        folder = filedialog.askdirectory(title="Ergebnisordner auswählen")
        if folder:
            self.output_dir.set(folder)

    def start_export(self):
        search = Path(self.search_dir.get())
        output = Path(self.output_dir.get())

        if not search.is_dir():
            messagebox.showerror("Fehler", "Bitte gültigen Suchordner auswählen.")
            return

        if not output.exists():
            try:
                output.mkdir(parents=True)
            except Exception as exc:
                messagebox.showerror(
                    "Fehler",
                    f"Ergebnisordner konnte nicht erstellt werden:\n{exc}"
                )
                return

        script = Path(__file__).with_name("export_all_diagrams.js")
        if not script.is_file():
            messagebox.showerror("Fehler", f"Script nicht gefunden:\n{script}")
            return

        self.start_button.config(state="disabled")
        self.config(cursor="watch")
        self.log.config(cursor="watch")
        self.update_idletasks()

        self.log.delete("1.0", "end")

        thread = threading.Thread(
            target=self.run_export,
            args=(search, output, script),
            daemon=True,
        )
        thread.start()

    def run_export(self, search: Path, output: Path, script: Path):
        files = [
            p for p in search.rglob("*")
            if p.is_file() and p.suffix.lower() in EA_EXTENSIONS
        ]

        self.write_log(f"Gefundene EA-Dateien: {len(files)}\n\n")

        if not files:
            self.write_log("Keine .qea/.qeax/.eap/.eapx/.feap Dateien gefunden.\n")
            self.done()
            return

        for index, ea_file in enumerate(files, start=1):
            self.write_log(f"[{index}/{len(files)}] {ea_file}\n")

            existing_folders = {p for p in output.iterdir() if p.is_dir()}

            cmd = [
                "cscript.exe",
                "//nologo",
                str(script),
                str(ea_file),
                str(output),
            ]

            try:
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding="mbcs" if sys.platform == "win32" else "utf-8",
                    errors="replace",
                )

                if proc.stdout:
                    self.write_log(proc.stdout)

                if proc.stderr:
                    self.write_log(proc.stderr)

                if proc.returncode != 0:
                    self.write_log(f"FEHLER: Returncode {proc.returncode}\n")

            except Exception as exc:
                self.write_log(f"FEHLER beim Ausführen: {exc}\n")

            if ea_file.suffix.lower() in QEA_EXTENSIONS:
                new_folders = {p for p in output.iterdir() if p.is_dir()} - existing_folders
                if new_folders:
                    model_out = new_folders.pop()
                else:
                    model_out = _unique_model_folder(output, ea_file.stem)
                    model_out.mkdir(parents=True, exist_ok=True)
                export_names_txt(ea_file, model_out, self.write_log)

            self.write_log("\n")

        self.write_log("Fertig.\n")
        self.done()

    def write_log(self, text: str):
        self.after(0, lambda: self._append_log(text))

    def _append_log(self, text: str):
        self.log.insert("end", text)
        self.log.see("end")

    def done(self):
        def reset_ui():
            self.start_button.config(state="normal")
            self.config(cursor="")
            self.log.config(cursor="")
            self.update_idletasks()

        self.after(0, reset_ui)


if __name__ == "__main__":
    App().mainloop()
