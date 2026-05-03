# ea_batch_export_gui.py
# Voraussetzung:
#   Windows
#   Sparx Enterprise Architect installiert und COM registriert
#   export_all_diagrams.js liegt im gleichen Ordner wie diese Python-Datei

import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

EA_EXTENSIONS = {".qea", ".qeax", ".eap", ".eapx", ".feap"}


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
                messagebox.showerror("Fehler", f"Ergebnisordner konnte nicht erstellt werden:\n{exc}")
                return

        script = Path(__file__).with_name("export_all_diagrams.js")
        if not script.is_file():
            messagebox.showerror("Fehler", f"Script nicht gefunden:\n{script}")
            return

        self.start_button.config(state="disabled")
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
                    encoding="mbcs",
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

            self.write_log("\n")

        self.write_log("Fertig.\n")
        self.done()

    def write_log(self, text: str):
        self.after(0, lambda: self._append_log(text))

    def _append_log(self, text: str):
        self.log.insert("end", text)
        self.log.see("end")

    def done(self):
        self.after(0, lambda: self.start_button.config(state="normal"))


if __name__ == "__main__":
    App().mainloop()
    