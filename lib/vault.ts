import fs from "node:fs";
import path from "node:path";

export type VaultEntry = {
  id: string;
  slug: string;
  title: string;
  authors: string[];
  authorLabel: string;
  publishedAt: string;
  sourceUrl: string | null;
  snippet: string;
  topic: string;
  folderPath: string;
  fileName: string;
  relativePath: string;
};

const VAULT_INDEX_PATH = path.join(process.cwd(), "content", "vault-index.json");

export function getVaultEntries(): VaultEntry[] {
  if (!fs.existsSync(VAULT_INDEX_PATH)) {
    return [];
  }

  const raw = fs.readFileSync(VAULT_INDEX_PATH, "utf8");

  return JSON.parse(raw) as VaultEntry[];
}
