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

export function activate(context: vscode.ExtensionContext): void {
  // --- LSP client ---
  const serverExecutable: Executable = {
    command: getExecutable(),
    args: ["lsp"],
  };

  const serverOptions: ServerOptions = {
    run: serverExecutable,
    debug: serverExecutable,
  };

  const clientOptions: LanguageClientOptions = {
    documentSelector: [{ scheme: "file", language: "ragul" }],
    synchronize: {
      fileEvents: vscode.workspace.createFileSystemWatcher("**/*.ragul"),
    },
  };

  client = new LanguageClient("ragul", "Ragul Language Server", serverOptions, clientOptions);
  client.start();

  // --- Commands ---
  context.subscriptions.push(
    vscode.commands.registerCommand("ragul.runFile", async () => {
      const editor = vscode.window.activeTextEditor;

      // If called from explorer context menu, use that file instead
      const file =
        editor?.document.languageId === "ragul"
          ? editor.document.fileName
          : undefined;

      if (!file) {
        vscode.window.showErrorMessage("Open a .ragul file to run it.");
        return;
      }

      // Save before running
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

  // Dispose terminal on deactivate
  context.subscriptions.push({ dispose: () => terminal?.dispose() });
}

export function deactivate(): Thenable<void> | undefined {
  return client?.stop();
}
