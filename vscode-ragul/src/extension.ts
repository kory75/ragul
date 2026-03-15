import * as vscode from "vscode";
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  Executable,
} from "vscode-languageclient/node";

let client: LanguageClient | undefined;
let terminal: vscode.Terminal | undefined;

function getExecutable(): string {
  return vscode.workspace.getConfiguration("ragul").get("executablePath") ?? "ragul";
}

function getOrCreateTerminal(): vscode.Terminal {
  if (!terminal || terminal.exitStatus !== undefined) {
    terminal = vscode.window.createTerminal("Ragul");
  }
  return terminal;
}

function startLspClient(context: vscode.ExtensionContext): void {
  const serverExecutable: Executable = {
    command: getExecutable(),
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

  // Start in the background — a missing/broken ragul binary must not
  // prevent the run/check commands from working.
  client.start().catch((err) => {
    console.warn("[ragul] LSP failed to start:", err);
  });

  context.subscriptions.push({ dispose: () => client?.stop() });
}

function disableSpellCheckerForRagul(): void {
  // Code Spell Checker reads cSpell.languageSettings — add ragul: disabled
  // if not already present. We write to Global so it applies everywhere.
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
      .then(undefined, () => {
        // cSpell not installed — ignore silently
      });
  }
}

export function activate(context: vscode.ExtensionContext): void {
  // --- Commands (registered first — independent of LSP) ---
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
      term.sendText(`${getExecutable()} futtat "${file}"`);
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
      term.sendText(`${getExecutable()} ellenőriz "${editor.document.fileName}"`);
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

  // --- LSP (started after commands — failures are non-fatal) ---
  startLspClient(context);

  // --- Suppress spell checker for .ragul files ---
  disableSpellCheckerForRagul();
}

export function deactivate(): Thenable<void> | undefined {
  return client?.stop();
}
