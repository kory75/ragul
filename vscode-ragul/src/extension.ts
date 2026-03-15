import * as vscode from "vscode";
import * as path from "path";
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  Executable,
} from "vscode-languageclient/node";

let client: LanguageClient | undefined;

export function activate(context: vscode.ExtensionContext): void {
  const config = vscode.workspace.getConfiguration("ragul");
  const executablePath: string = config.get("executablePath") ?? "ragul";

  const serverExecutable: Executable = {
    command: executablePath,
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

  client = new LanguageClient(
    "ragul",
    "Ragul Language Server",
    serverOptions,
    clientOptions
  );

  client.start();

  context.subscriptions.push(
    vscode.commands.registerCommand("ragul.restartServer", async () => {
      if (client) {
        await client.stop();
        await client.start();
        vscode.window.showInformationMessage("Ragul language server restarted.");
      }
    })
  );
}

export function deactivate(): Thenable<void> | undefined {
  return client?.stop();
}
