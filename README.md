# manageSparxRepos
manage the Sparx repositories that are gambling around the disk

# Sparx EA Batch Export Tool

Dieses Tool ermöglicht die automatisierte Verarbeitung von Sparx Enterprise Architect Modellen (`.qea`, `.qeax`, `.eap`, `.eapx`, `.feap`):

- **Diagrammexport** (Windows): exportiert alle Diagramme als PNG über die EA-Automation
- **Elementauswertung** (plattformübergreifend): liest die `t_object`-Tabelle direkt aus `.qea`-Dateien (SQLite) und erzeugt pro Modell eine `names.txt`

Die Lösung besteht aus zwei Komponenten:

- **JScript (Windows Script Host)**: führt den Diagrammexport über die EA-Automation aus
- **Python GUI Tool**: durchsucht Ordner rekursiv, startet den Export und erstellt die Elementauswertung

---
![managesparxrepos screenshot](Screenshot%202026-05-03%20092257.png)
---

## Funktionen
### 1. Diagrammexport

- Exportiert alle Diagramme eines Modells
- Unterstützt alle EA-Diagrammtypen, z. B.:
  - UML
  - BPMN
  - ArchiMate
- Exportiert als PNG-Dateien

### 2. Unterstützung von Element-Diagrammen

Zusätzlich werden Diagramme exportiert, die direkt unter Elementen liegen, z. B.:

- Activities
- BusinessProcesses
- BPMN-Elemente
- beliebige andere Elemente

Diese Diagramme liegen oft nicht direkt in Packages und werden deshalb gesondert rekursiv gesucht.

### 3. Strukturierter Export

Die Ausgabe erfolgt strukturiert nach Modell, Package und Elementpfad.

Beispiel:

    <Zielordner>
     └── <Modellname>
          └── <Package>
               └── <SubPackage>
                    └── <Element>
                         └── Diagramm.png

### 4. Eindeutige Dateinamen

Dateinamen enthalten:

- Package- bzw. Elementpfad
- Diagrammtitel
- Diagramm-ID

Beispiel:

    Business__OrderProcessing__Process1__MyDiagram__ID-123.png

### 5. Batch-Verarbeitung

Das Python-Tool:

- durchsucht rekursiv einen Ordner
- findet alle EA-Dateien
- führt den Export automatisch für jede gefundene Datei aus

### 6. GUI

Die Python-GUI bietet:

- Auswahl des Suchordners
- Auswahl des Zielordners
- Start-Button
- Live-Log
- Wait-Cursor während der Verarbeitung

### 7. Robuste Ordnererzeugung

Das JScript:

- unterstützt lokale Pfade wie `C:\...`
- unterstützt UNC-Pfade wie `\\server\share`
- erstellt Ordner rekursiv
- vermeidet Namenskonflikte

### 8. Fehlerbehandlung

Das Tool protokolliert:

- fehlgeschlagene Diagrammexporte
- Datei- und Pfadprobleme
- Returncodes des JScript-Aufrufs

Bei einzelnen Fehlern läuft der Batch-Export weiter.

### 9. Elementauswertung – `names.txt`

Für jede `.qea`-Datei wird die SQLite-Tabelle `t_object` ausgewertet und eine CSV-Datei `names.txt` im Modell-Ausgabeordner erzeugt.

- Trennzeichen: `;`
- Kodierung: UTF-8
- Spalten: `Name;ea_guid;Stereotype;Notes;Datum`
- Läuft **ohne EA-Installation**, auch auf Linux und macOS
- `Datum` enthält das Datum der letzten Änderung des Elements (ohne Uhrzeit)

Beispiel:

    Name;ea_guid;Stereotype;Notes;Datum
    OrderProcess;{A1B2C3D4-...};BPMN2.0;Hauptprozess;2026-04-15
    PaymentService;{E5F6G7H8-...};;;2026-03-01

---

## Voraussetzungen

### Diagrammexport (Windows only)

- Windows
- Sparx Enterprise Architect installiert
- EA-COM-Schnittstelle verfügbar

### Elementauswertung `names.txt` (plattformübergreifend)

- Windows, Linux oder macOS
- Python 3.x
- keine zusätzlichen Python-Pakete erforderlich

### Python GUI

- Python 3.x mit `tkinter`
- keine zusätzlichen Python-Pakete erforderlich

---

## Projektstruktur

    /projekt
     ├── export_all_diagrams.js
     ├── ea_batch_export_gui.py
     └── README.md

---

## Verwendung

### 1. Python starten

    python ea_batch_export_gui.py

### 2. In der GUI auswählen

1. Ordner zur Durchsuchung wählen
2. Zielordner wählen
3. Export starten

### 3. Ablauf

Das Tool:

1. findet rekursiv alle EA-Dateien
2. startet für jede Datei das JScript (nur Windows)
3. öffnet das Modell über EA-Automation und exportiert alle Diagramme
4. liest für `.qea`-Dateien die `t_object`-Tabelle per SQLite und schreibt `names.txt`
5. legt alle Ergebnisse im Zielordner ab

---

## Technische Details

### JScript

Das JScript nutzt:

- `EA.Repository`
- `Repository.OpenFile`
- `Repository.GetProjectInterface`
- `Project.PutDiagramImageToFile`

Die Traversierung erfolgt rekursiv über:

- Models
- Packages
- Package-Diagramme
- Package-Elemente
- Element-Diagramme
- Kind-Elemente

### Python

Das Python-Programm nutzt:

- `tkinter` für die GUI
- `threading`, damit die Oberfläche während des Exports responsiv bleibt
- `subprocess`, um `cscript.exe` mit dem JScript zu starten (nur Windows)
- `sqlite3`, um `.qea`-Dateien direkt zu lesen und `names.txt` zu erzeugen
- `csv`, um die Ausgabe als semikolongetrennte CSV-Datei zu schreiben
- `pathlib`, um Pfade und Dateisuche zu behandeln

---

## Unterstützte Dateitypen

Das Python-Tool sucht nach:

- `.qea`
- `.qeax`
- `.eap`
- `.eapx`
- `.feap`

---

## Ausgabeformat

### Diagramme

Der Diagrammexport erfolgt als PNG. Die Dateinamen werden bereinigt, damit sie unter Windows gültig sind. Ungültige Zeichen werden ersetzt:

    < > : " / \ | ? *

### Elementauswertung

Pro `.qea`-Datei wird eine `names.txt` im Modell-Ausgabeordner erzeugt:

    Name;ea_guid;Stereotype;Notes;Datum
    OrderProcess;{A1B2C3D4-...};BPMN2.0;Hauptprozess;2026-04-15
    PaymentService;{E5F6G7H8-...};;;2026-03-01

---

## Erweiterungsmöglichkeiten

Mögliche spätere Erweiterungen:

- Export als SVG oder PDF
- Filter nach Diagrammtypen
- Filter nur für BPMN-Diagramme
- Fortschrittsbalken mit Prozentanzeige
- Logdatei zusätzlich zum GUI-Log
- konfigurierbare Naming-Konvention
- Exportbericht als CSV oder HTML
- Auswahl, ob vorhandene Exportordner überschrieben oder versioniert werden sollen

---

## Hinweise

- Große Modelle können längere Laufzeiten verursachen.
- EA wird für jede gefundene Modelldatei über Automation geöffnet.
- Schreibrechte im Zielordner sind erforderlich.
- Die `names.txt`-Auswertung funktioniert ohne EA und auch auf Linux/macOS.
- Bei UNC-Pfaden muss die Basisfreigabe bereits existieren.
- Bestehende Modellordner werden nicht überschrieben, sondern mit Suffix wie `_2`, `_3` usw. neu angelegt.

---

## Typische Use Cases

- Dokumentation von Architekturmodellen
- Export von BPMN-Prozessdiagrammen
- Übergabe an externe Stakeholder
- Archivierung von Modellständen
- Review- und Audit-Vorbereitung
- schnelle Sichtprüfung großer Modellbestände
