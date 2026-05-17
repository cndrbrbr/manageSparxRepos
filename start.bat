@echo off
setlocal

echo ==========================================
echo   manageSparxRepos - EA Batch Export Tool
echo ==========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo FEHLER: Python wurde nicht gefunden.
    echo.
    echo Bitte Python 3 installieren und sicherstellen,
    echo dass 'python' im PATH verfuegbar ist.
    echo.
    pause
    exit /b 1
)

if not exist ea_batch_export_gui.py (
    echo FEHLER: ea_batch_export_gui.py wurde nicht gefunden.
    echo.
    echo Bitte start.bat aus dem Projektordner starten.
    echo.
    pause
    exit /b 1
)

echo Starte GUI...
echo.

python ea_batch_export_gui.py

if errorlevel 1 (
    echo.
    echo Das Programm wurde mit Fehler beendet.
    pause
)

endlocal