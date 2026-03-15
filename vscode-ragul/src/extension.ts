import * as vscode from "vscode";
import * as cp from "child_process";
import * as fs from "fs";
import * as path from "path";
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  Executable,
} from "vscode-languageclient/node";

let client: LanguageClient | undefined;
let terminal: vscode.Terminal | undefined;
let resolvedExecutable: string = "ragul";

/** Scan common Windows/macOS/Linux locations for the ragul script. */
function detectRagulExecutable(): string {
  const configured = vscode.workspace
    .getConfiguration("ragul")
    .get<string>("executablePath");
  if (configured && configured !== "ragul") {
    return configured;
  }

  // 1. Try via child_process (works when Python is on PATH)
  const pyScript = [
    "import sys, pathlib",
    "s = pathlib.Path(sys.executable).parent",
    "found = next((str(s/f'ragul{e}') for e in ['','.exe','.cmd'] if (s/f'ragul{e}').exists()), '')",
    "print(found)",
  ].join("; ");

  for (const py of ["python", "python3", "py"]) {
    try {
      const out = cp
        .execSync(`${py} -c "${pyScript}"`, { encoding: "utf8", timeout: 3000 })
        .trim();
      if (out && fs.existsSync(out)) {
        return out;
      }
    } catch {
      // try next
    }
  }

  // 2. Scan common Windows Python user-install locations
  const appData = process.env["APPDATA"] ?? "";
  const localAppData = process.env["LOCALAPPDATA"] ?? "";

  const windowsRoots = [
    path.join(appData, "Python"),
    path.join(localAppData, "Programs", "Python"),
    path.join(localAppData, "Python"),
    "C:\\Python313",
    "C:\\Python312",
    "C:\\Python311",
  ];

  for (const root of windowsRoots) {
    if (!fs.existsSync(root)) {
      continue;
    }
    // May be versioned subdirectory (Python313, Python312, …) or the root itself
    const subdirs = [root, ...fs.readdirSync(root).map((d) => path.join(root, d))];
    for (const dir of subdirs) {
      for (const name of ["ragul.EXE", "ragul.exe", "ragul.cmd", "ragul"]) {
        const candidate = path.join(dir, "Scripts", name);
        if (fs.existsSync(candidate)) {
          return candidate;
        }
      }
    }
  }

  // 3. macOS/Linux: check common venv and pipx locations
  const home = process.env["HOME"] ?? "";
  const unixRoots = [
    path.join(home, ".local", "bin", "ragul"),
    path.join(home, ".local", "pipx", "venvs", "ragul-lang", "bin", "ragul"),
    "/usr/local/bin/ragul",
    "/usr/bin/ragul",
  ];
  for (const candidate of unixRoots) {
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }

  return "ragul";
}

function getOrCreateTerminal(): vscode.Terminal {
  if (!terminal || terminal.exitStatus !== undefined) {
    terminal = vscode.window.createTerminal("Ragul");
  }
  return terminal;
}

function startLspClient(context: vscode.ExtensionContext): void {
  const serverExecutable: Executable = {
    command: resolvedExecutable,
    args: ["lsp"],
  };

  const clientOptions: LanguageClientOptions = {
    documentSelector: [{ scheme: "file", language: "ragul" }],
    synchronize: {
      fileEvents: vscode.workspace.createFileSystemWatcher("**/*.ragul"),
    },
  };

  client = new LanguageClient(
    "ragul",
    "Ragul Language Server",
    { run: serverExecutable, debug: serverExecutable },
    clientOptions
  );

  client.start().catch((err) => {
    console.warn("[ragul] LSP failed to start:", err);
  });

  context.subscriptions.push({ dispose: () => client?.stop() });
}

function disableSpellCheckerForRagul(): void {
  const config = vscode.workspace.getConfiguration("cSpell");
  const settings: { languageId: string; enabled: boolean }[] =
    config.get("languageSettings") ?? [];

  if (!settings.some((s) => s.languageId === "ragul")) {
    config
      .update(
        "languageSettings",
        [...settings, { languageId: "ragul", enabled: false }],
        vscode.ConfigurationTarget.Global
      )
      .then(undefined, () => {});
  }
}

export function activate(context: vscode.ExtensionContext): void {
  resolvedExecutable = detectRagulExecutable();
  console.log(`[ragul] using executable: ${resolvedExecutable}`);

  // --- Commands ---
  context.subscriptions.push(
    vscode.commands.registerCommand("ragul.runFile", async () => {
      const editor = vscode.window.activeTextEditor;
      const file =
        editor?.document.languageId === "ragul"
          ? editor.document.fileName
          : undefined;

      if (!file) {
        vscode.window.showErrorMessage("Open a .ragul file to run it.");
        return;
      }

      await editor?.document.save();
      const term = getOrCreateTerminal();
      term.show(true);
      term.sendText(`& "${resolvedExecutable}" futtat "${file}"`);
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("ragul.checkFile", async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor || editor.document.languageId !== "ragul") {
        vscode.window.showErrorMessage("Open a .ragul file to check it.");
        return;
      }

      await editor.document.save();
      const term = getOrCreateTerminal();
      term.show(true);
      term.sendText(
        `& "${resolvedExecutable}" ellenőriz "${editor.document.fileName}"`
      );
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("ragul.restartServer", async () => {
      if (client) {
        await client.stop();
        await client.start();
        vscode.window.showInformationMessage("Ragul language server restarted.");
      }
    })
  );

  context.subscriptions.push({ dispose: () => terminal?.dispose() });

  startLspClient(context);
  disableSpellCheckerForRagul();
}

export function deactivate(): Thenable<void> | undefined {
  return client?.stop();
}
