# manageSparxRepos
manage the Sparx repositories that are gambling around the disk

# Sparx EA Diagram Export Tool

Dieses Tool ermöglicht den automatisierten Export aller Diagramme aus Sparx Enterprise Architect Modellen (`.qea`, `.qeax`, `.eap`, `.eapx`, `.feap`), inklusive BPMN-Diagrammen, die unter Elementen wie Aktivitäten oder Businessprozessen hängen.

Die Lösung besteht aus zwei Komponenten:

- **JScript (Windows Script Host)**: führt den Export über die EA-Automation aus
- **Python GUI Tool**: durchsucht Ordner rekursiv und startet den Export für alle Modelle

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

---

## Voraussetzungen

### System

- Windows
- Sparx Enterprise Architect installiert
- EA-COM-Schnittstelle verfügbar

### Python

- Python 3.x
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
2. startet für jede Datei das JScript
3. öffnet das Modell über EA-Automation
4. exportiert alle Package- und Element-Diagramme
5. legt die Ergebnisse im Zielordner ab

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
- `subprocess`, um `cscript.exe` mit dem JScript zu starten
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

Der Diagrammexport erfolgt als:

- PNG

Die Dateinamen werden bereinigt, damit sie unter Windows gültig sind.

Ungültige Zeichen wie diese werden ersetzt:

    < > : " / \ | ? *

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
