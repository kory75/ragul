import * as vscode from "vscode";
import * as cp from "child_process";
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  Executable,
} from "vscode-languageclient/node";

let client: LanguageClient | undefined;
let terminal: vscode.Terminal | undefined;
let resolvedExecutable: string = "ragul";

/** Try to find the ragul executable via Python's scripts directory. */
function detectRagulExecutable(): string {
  const configured = vscode.workspace
    .getConfiguration("ragul")
    .get<string>("executablePath");
  if (configured && configured !== "ragul") {
    return configured;
  }

  // Ask Python where its Scripts folder is and look for ragul[.exe/.cmd] there.
  const script = [
    "import sys, pathlib",
    "scripts = pathlib.Path(sys.executable).parent",
    "found = next((str(scripts / f'ragul{e}') for e in ['', '.exe', '.cmd'] if (scripts / f'ragul{e}').exists()), '')",
    "print(found)",
  ].join("; ");

  for (const py of ["python", "python3", "py"]) {
    try {
      const result = cp
        .execSync(`${py} -c "${script}"`, { encoding: "utf8", timeout: 3000 })
        .trim();
      if (result) {
        return result;
      }
    } catch {
      // try next
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
