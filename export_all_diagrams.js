// export_all_diagrams.js
// Aufruf:
// cscript //nologo export_all_diagrams.js "C:\Modelle\abc.qea" "C:\ExportRoot"

var XMI_TYPE_EA_11 = 3;
var XMI_TYPE_NATIVE = 24;

function main() {
    if (WScript.Arguments.length < 2) {
        WScript.Echo("Usage: cscript //nologo export_all_diagrams.js <ea-file> <output-root>");
        WScript.Quit(2);
    }

    var modelFile = WScript.Arguments(0);
    var outputRoot = WScript.Arguments(1);

    var fso = new ActiveXObject("Scripting.FileSystemObject");

    if (!fso.FileExists(modelFile)) {
        WScript.Echo("EA-Datei nicht gefunden: " + modelFile);
        WScript.Quit(3);
    }

    ensureFolder(outputRoot);

    var modelName = sanitizeFileName(fso.GetBaseName(modelFile));
    var modelOut = buildUniqueFolder(outputRoot, modelName);
    ensureFolder(modelOut);

    var repo = null;

    try {
        repo = new ActiveXObject("EA.Repository");

        WScript.Echo("Oeffne: " + modelFile);

        if (!repo.OpenFile(modelFile)) {
            throw new Error("OpenFile fehlgeschlagen: " + modelFile);
        }

        var project = repo.GetProjectInterface();
        var count = 0;
        var xmiCount = 0;

        for (var i = 0; i < repo.Models.Count; i++) {
            var root = repo.Models.GetAt(i);
            xmiCount += exportPackagesBelowModelXMI(project, root, modelOut);
            count += exportPackageRecursive(repo, project, root, modelOut, "");
        }

        WScript.Echo("Exportiert: " + count + " Diagramme nach " + modelOut);
        WScript.Echo("Exportiert: " + xmiCount + " Package-XMI-Dateien nach " + modelOut + "\\xmi");

        repo.CloseFile();
        repo.Exit();
        repo = null;

        WScript.Quit(0);

    } catch (e) {
        WScript.Echo("FEHLER: " + e.message);

        try {
            if (repo != null) {
                repo.CloseFile();
                repo.Exit();
            }
        } catch (ignore) {}

        WScript.Quit(1);
    }
}

function exportPackagesBelowModelXMI(project, modelPkg, modelOut) {
    var count = 0;
    var modelName = sanitizeFileName(modelPkg.Name);
    if (modelName.length == 0) {
        modelName = "Model_" + modelPkg.PackageID;
    }

    for (var p = 0; p < modelPkg.Packages.Count; p++) {
        var child = modelPkg.Packages.GetAt(p);
        count += exportPackageAndChildrenXMI(project, child, modelOut, modelName);
    }

    return count;
}

function exportPackageAndChildrenXMI(project, pkg, modelOut, parentPath) {
    var packageName = sanitizeFileName(pkg.Name);
    if (packageName.length == 0) {
        packageName = "Package_" + pkg.PackageID;
    }

    var packagePath = parentPath && parentPath.length > 0
        ? parentPath + "\\" + packageName
        : packageName;

    var count = 0;

    if (exportPackageXMI(project, pkg, modelOut, packagePath, XMI_TYPE_EA_11, "XMI-1.1", "xmi11")) {
        count++;
    }

    if (exportPackageXMI(project, pkg, modelOut, packagePath, XMI_TYPE_NATIVE, "Native", "native")) {
        count++;
    }

    for (var p = 0; p < pkg.Packages.Count; p++) {
        var child = pkg.Packages.GetAt(p);
        count += exportPackageAndChildrenXMI(project, child, modelOut, packagePath);
    }

    return count;
}

function exportPackageXMI(project, pkg, modelOut, packagePath, xmiType, label, folderName) {
    var fso = new ActiveXObject("Scripting.FileSystemObject");

    var exportFolder = fso.BuildPath(modelOut, "xmi");
    exportFolder = fso.BuildPath(exportFolder, folderName);
    ensureFolder(exportFolder);

    var fileBase = sanitizeFileName(packagePath.replace(/\\/g, "__"));
    if (fileBase.length == 0) {
        fileBase = "Package_" + pkg.PackageID;
    }

    var outFile = fso.BuildPath(exportFolder, fileBase + "__" + label + ".xml");
    outFile = avoidOverwrite(outFile);

    try {
        WScript.Echo("Exportiere Package als " + label + ": " + packagePath);
        WScript.Echo("Nach: " + outFile);

        // ExportPackageXMI erwartet die Package-GUID im XML-Format.
        // xmiEA11 = 3, xmiNative = 24, DiagramXML = 1, DiagramImage = -1, FormatXML = 1, UseDTD = 0.
        var result = project.ExportPackageXMI(
            project.GUIDtoXML(pkg.PackageGUID),
            xmiType,
            1,
            -1,
            1,
            0,
            outFile
        );

        if (result != null && String(result).length > 0) {
            WScript.Echo(label + " Export Ergebnis: " + result);
        }

        if (!fso.FileExists(outFile)) {
            WScript.Echo("WARNUNG: " + label + " Datei wurde nicht erstellt: " + outFile);
            return false;
        }

        return true;

    } catch (e) {
        WScript.Echo("WARNUNG: Fehler beim " + label + " Export von Package '" + packagePath + "': " + e.message);
        return false;
    }
}

function exportPackageRecursive(repo, project, pkg, modelOut, parentPath) {
    var fso = new ActiveXObject("Scripting.FileSystemObject");
    var count = 0;

    var packageName = sanitizeFileName(pkg.Name);
    if (packageName.length == 0) {
        packageName = "Package_" + pkg.PackageID;
    }

    var thisPath = parentPath && parentPath.length > 0
        ? parentPath + "\\" + packageName
        : packageName;

    var folder = fso.BuildPath(modelOut, thisPath);
    ensureFolder(folder);

    for (var d = 0; d < pkg.Diagrams.Count; d++) {
        var dia = pkg.Diagrams.GetAt(d);

        var diaName = sanitizeFileName(dia.Name);
        if (diaName.length == 0) {
            diaName = "Diagram_" + dia.DiagramID;
        }

        var flatPkgPath = sanitizeFileName(thisPath.replace(/\\/g, "__"));
        var fileName = flatPkgPath + "__" + diaName + "__ID-" + dia.DiagramID + ".png";
        var outFile = fso.BuildPath(folder, fileName);

        outFile = avoidOverwrite(outFile);

        try {
            WScript.Echo("Exportiere Diagramm: " + dia.Name);
            WScript.Echo("Nach: " + outFile);

            repo.OpenDiagram(dia.DiagramID);

            // 1 = Format anhand Dateiendung, hier .png
            var ok = project.PutDiagramImageToFile(dia.DiagramGUID, outFile, 1);

            repo.CloseDiagram(dia.DiagramID);

            if (!ok) {
                WScript.Echo("WARNUNG: Export fehlgeschlagen: " + dia.Name);
            } else {
                count++;
            }

        } catch (e) {
            WScript.Echo("WARNUNG: Fehler bei Diagramm '" + dia.Name + "': " + e.message);
            try {
                repo.CloseDiagram(dia.DiagramID);
            } catch (ignore) {}
        }
    }

    for (var p = 0; p < pkg.Packages.Count; p++) {
        var child = pkg.Packages.GetAt(p);
        count += exportPackageRecursive(repo, project, child, modelOut, thisPath);
    }

    return count;
}

function ensureFolder(path) {
    var fso = new ActiveXObject("Scripting.FileSystemObject");

    path = String(path).replace(/\//g, "\\");
    if (fso.FolderExists(path)) return;

    var parts = path.split("\\");
    var current = "";

    // UNC-Pfad behandeln: \\server\share\...
    if (path.indexOf("\\\\") == 0) {
        current = "\\\\";
        var uncParts = [];

        for (var u = 0; u < parts.length; u++) {
            if (parts[u] != "") {
                uncParts.push(parts[u]);
            }
        }

        if (uncParts.length < 2) {
            throw new Error("Ungueltiger UNC-Pfad: " + path);
        }

        current = "\\\\" + uncParts[0] + "\\" + uncParts[1];

        if (!fso.FolderExists(current)) {
            throw new Error("UNC-Basis existiert nicht: " + current);
        }

        for (var ui = 2; ui < uncParts.length; ui++) {
            current = current + "\\" + uncParts[ui];
            if (!fso.FolderExists(current)) {
                WScript.Echo("Erzeuge Ordner: " + current);
                fso.CreateFolder(current);
            }
        }

        return;
    }

    // Laufwerk behandeln, z. B. C:
    if (parts.length > 0 && parts[0].match(/^[A-Za-z]:$/)) {
        current = parts[0] + "\\";
        parts.shift();
    }

    for (var i = 0; i < parts.length; i++) {
        if (parts[i] == "") continue;

        if (current == "" || current.match(/\\$/)) {
            current = current + parts[i];
        } else {
            current = current + "\\" + parts[i];
        }

        if (!fso.FolderExists(current)) {
            WScript.Echo("Erzeuge Ordner: " + current);
            fso.CreateFolder(current);
        }
    }
}

function sanitizeFileName(name) {
    if (name == null) return "";

    var s = String(name);

    s = s.replace(/[<>:"\/\\|?*\x00-\x1F]/g, "_");
    s = s.replace(/\s+/g, " ");
    s = s.replace(/^\s+|\s+$/g, "");
    s = s.replace(/\.+$/g, "");

    if (s.length > 120) {
        s = s.substring(0, 120);
    }

    return s;
}

function buildUniqueFolder(root, baseName) {
    var fso = new ActiveXObject("Scripting.FileSystemObject");

    root = String(root).replace(/\//g, "\\");
    baseName = sanitizeFileName(baseName);

    if (baseName.length == 0) {
        baseName = "EA_Model";
    }

    var folder = fso.BuildPath(root, baseName);
    var i = 2;

    while (fso.FolderExists(folder)) {
        folder = fso.BuildPath(root, baseName + "_" + i);
        i++;
    }

    return folder;
}

function avoidOverwrite(path) {
    var fso = new ActiveXObject("Scripting.FileSystemObject");

    if (!fso.FileExists(path)) {
        return path;
    }

    var folder = fso.GetParentFolderName(path);
    var base = fso.GetBaseName(path);
    var ext = fso.GetExtensionName(path);
    var i = 2;

    var candidate;

    do {
        candidate = fso.BuildPath(folder, base + "_" + i + "." + ext);
        i++;
    } while (fso.FileExists(candidate));

    return candidate;
}

main();