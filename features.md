# Features – manageSparxRepos

## Bestehende Features

### 1. Diagrammexport (`export_all_diagrams.js` + `ea_batch_export_gui.py`)

Exportiert alle Diagramme aus Sparx-EA-Modellen automatisiert als PNG-Dateien.

**Umfang:**
- Unterstützte Dateiformate: `.qea`, `.qeax`, `.eap`, `.eapx`, `.feap`
- Alle Diagrammtypen (UML, BPMN, ArchiMate, etc.)
- Diagramme direkt unter Paketen **und** unter Elementen (Activities, BusinessProcesses, BPMN-Elemente, …)
- Strukturierte Ausgabe nach Modell → Package → SubPackage → Element
- Eindeutige Dateinamen aus Pfad, Titel und Diagramm-ID
- Rekursive Batch-Verarbeitung ganzer Ordnerbäume
- Python-GUI mit Ordnerauswahl, Start-Button und Live-Log
- Robuste Ordnererzeugung für lokale Pfade und UNC-Pfade
- Fehlerbehandlung: einzelne Fehler stoppen den Gesamtlauf nicht

---

## Geplante Features

### 2. Auswertung der `t_object`-Tabelle – Export als `names.txt`

**Zweck:**  
Pro verarbeiteter QEA-Datei wird die interne SQLite-Tabelle `t_object` ausgewertet und eine CSV-Datei `names.txt` erzeugt. Diese enthält eine flache Übersicht aller Modellelemente mit ihren wesentlichen Metadaten.

**Ausgabedatei:** `names.txt`  
**Trennzeichen:** `;`  
**Kodierung:** UTF-8

**Spalten (Reihenfolge):**

| Spalte      | Quelle in `t_object` | Beschreibung                          |
|-------------|----------------------|---------------------------------------|
| `Name`      | `Name`               | Name des Elements                     |
| `ea_guid`   | `ea_guid`            | Global eindeutige ID des Elements     |
| `Stereotype`| `Stereotype`         | Zugewiesener Stereotype (kann leer sein) |
| `Notes`     | `Note`               | Notiztext des Elements (kann leer sein) |
| `Datum`     | `ModifiedDate`       | Datum der letzten Änderung (nur Datum, ohne Uhrzeit) |

**Beispielzeile:**

```
Name;ea_guid;Stereotype;Notes;Datum
OrderProcess;{A1B2C3D4-...};BPMN2.0;Hauptprozess für Bestellungen;2026-04-15
PaymentService;{E5F6G7H8-...};;;2026-03-01
```

**Verhalten:**
- Die Datei `names.txt` wird in denselben Ausgabeordner geschrieben wie die Diagramme des jeweiligen Modells.
- Enthält ein Feld Semikolons oder Zeilenumbrüche, wird der Feldinhalt in doppelte Anführungszeichen eingeschlossen.
- Die erste Zeile ist immer der Header (`Name;ea_guid;Stereotype;Notes;Datum`).
- QEA-Dateien sind SQLite-Datenbanken und werden direkt per `sqlite3` abgefragt – **ohne** EA-Automation.
- Dadurch ist diese Auswertung unabhängig von einer installierten EA-Lizenz und kann auch auf Linux/macOS laufen.

**Technische Umsetzung (Python):**

```python
import sqlite3
import csv
from pathlib import Path

def export_names_txt(qea_file: Path, output_dir: Path) -> None:
    out_file = output_dir / "names.txt"
    con = sqlite3.connect(qea_file)
    try:
        cur = con.execute(
            "SELECT Name, ea_guid, Stereotype, Note, DATE(ModifiedDate) FROM t_object ORDER BY Name"
        )
        with open(out_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["Name", "ea_guid", "Stereotype", "Notes", "Datum"])
            writer.writerows(cur.fetchall())
    finally:
        con.close()
```

**Integration in den Batch-Ablauf:**  
Die Funktion wird in `ea_batch_export_gui.py` aufgerufen, nachdem der Diagrammexport für eine EA-Datei abgeschlossen ist (oder als eigenständiger Schritt, falls die Datei kein vollständiges EA-Automation-Export erlaubt).

**Voraussetzungen:**
- Python 3.x mit Standardbibliothek (`sqlite3`, `csv`)
- Keine zusätzlichen Pakete erforderlich
- Nur für `.qea`-Dateien (SQLite-Format); `.eap`/`.eapx` nutzen ein anderes Datenbankformat

---

## Erweiterungsmöglichkeiten

- Filter nach Elementtyp (`Object_Type` in `t_object`)
- Optionaler Export weiterer Felder (z. B. `Alias`, `Author`, `Status`, `Modified`)
- Zusammenführung aller `names.txt`-Dateien eines Batch-Laufs in eine Gesamtdatei
- Export als HTML-Tabelle oder Excel-Datei
- Fortschrittsbalken mit Prozentanzeige
- Konfigurierbare Auswahl der zu exportierenden Spalten via GUI
