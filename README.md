# manageSparxRepos
manage the Sparx repositories that are gambling around the disk

# Sparx EA Batch Export Tool

Dieses Tool ermöglicht die automatisierte Verarbeitung von Sparx Enterprise Architect Modellen (`.qea`, `.qeax`, `.eap`, `.eapx`, `.feap`):

- **Diagrammexport** (Windows): exportiert alle Diagramme als PNG über die EA-Automation
- **Rekursiver Package-XMI-Export** (Windows): exportiert alle Packages unterhalb der Models zusätzlich als XMI-Dateien
- **Elementauswertung** (plattformübergreifend): liest die `t_object`-Tabelle direkt aus `.qea`-Dateien (SQLite) und erzeugt pro Modell eine `names.txt`

Die Lösung besteht aus zwei Komponenten:

- **JScript (Windows Script Host)**: führt den Diagrammexport und die XMI-Exporte über die EA-Automation aus
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

### 2. Rekursiver Package-XMI-Export

Zusätzlich werden alle Packages unterhalb der Root-Models rekursiv als XMI-Dateien exportiert.

Für jedes Package werden zwei Exportformate erzeugt:

- XMI 1.1 (`xmiEA11`)
- Native EA XML (`xmiNative`)

Der Export erfolgt über die EA-Automation mit:

- `Project.ExportPackageXMI(...)`

Die Dateien werden in getrennten Ordnern abgelegt:

```text
<Modellordner>\xmi\xmi11
<Modellordner>\xmi\native
```

Dateinamen enthalten den vollständigen Package-Pfad, damit keine Namenskollisionen entstehen.

Beispiel:

```text
Export/
 └── MeinRepository/
      └── xmi/
           ├── xmi11/
           │    ├── Business__Applications__CRM__XMI-1.1.xml
           │    └── Business__Processes__Order__XMI-1.1.xml
           │
           └── native/
                ├── Business__Applications__CRM__Native.xml
                └── Business__Processes__Order__Native.xml
```

Eigenschaften:

- rekursiver Export aller Unterpackages
- robuste Fehlerbehandlung pro Package
- vorhandene Dateien werden nicht überschrieben
- geeignet für Versionsverwaltung und Package-basierte Archivierung

### 3. Unterstützung von Element-Diagrammen

Zusätzlich werden Diagramme exportiert, die direkt unter Elementen liegen, z. B.:

- Activities
- BusinessProcesses
- BPMN-Elemente
- beliebige andere Elemente

Diese Diagramme liegen oft nicht direkt in Packages und werden deshalb gesondert rekursiv gesucht.

### 4. Strukturierter Export

Die Ausgabe erfolgt strukturiert nach Modell, Package und Elementpfad.

Beispiel:

```text
<Zielordner>
 └── <Modellname>
      └── <Package>
           └── <SubPackage>
                └── <Element>
                     └── Diagramm.png
```

### 5. Eindeutige Dateinamen

Dateinamen enthalten:

- Package- bzw. Elementpfad
- Diagrammtitel
- Diagramm-ID

Beispiel:

```text
Business__OrderProcessing__Process1__MyDiagram__ID-123.png
```

### 6. Batch-Verarbeitung

Das Python-Tool:

- durchsucht rekursiv einen Ordner
- findet alle EA-Dateien
- führt den Export automatisch für jede gefundene Datei aus

### 7. GUI

Die Python-GUI bietet:

- Auswahl des Suchordners
- Auswahl des Zielordners
- Start-Button
- Live-Log
- Wait-Cursor während der Verarbeitung

Zusätzlich kann das Tool direkt über `start.bat` gestartet werden.

### 8. Robuste Ordnererzeugung

Das JScript:

- unterstützt lokale Pfade wie `C:\...`
- unterstützt UNC-Pfade wie `\\server\share`
- erstellt Ordner rekursiv
- vermeidet Namenskonflikte

### 9. Fehlerbehandlung

Das Tool protokolliert:

- fehlgeschlagene Diagrammexporte
- fehlgeschlagene XMI-Exporte
- Datei- und Pfadprobleme
- Returncodes des JScript-Aufrufs

Bei einzelnen Fehlern läuft der Batch-Export weiter.

### 10. Elementauswertung – `names.txt`

Für jede `.qea`-Datei wird die SQLite-Tabelle `t_object` ausgewertet und eine CSV-Datei `names.txt` im Modell-Ausgabeordner erzeugt.

- Trennzeichen: `;`
- Kodierung: UTF-8
- Spalten: `Name;ea_guid;Stereotype;Notes;Datum`
- Läuft **ohne EA-Installation**, auch auf Linux und macOS
- `Datum` enthält das Datum der letzten Änderung des Elements (ohne Uhrzeit)

Beispiel:

```text
Name;ea_guid;Stereotype;Notes;Datum
OrderProcess;{A1B2C3D4-...};BPMN2.0;Hauptprozess;2026-04-15
PaymentService;{E5F6G7H8-...};;;2026-03-01
```

## Starten

### Windows GUI starten

Einfach per Doppelklick:

```text
start.bat
```

oder manuell:

```bash
python ea_batch_export_gui.py
```

### Direktes Script starten

```cmd
cscript //nologo export_all_diagrams.js "C:\Modelle\abc.qea" "C:\ExportRoot"
```
