import { VaultWorkspace } from "@/components/vault-workspace";
import { getVaultEntries } from "@/lib/vault";

export default function VaultPage() {
  const entries = getVaultEntries();

  return <VaultWorkspace entries={entries} />;
}
