import { VaultWorkspace } from "@/components/vault-workspace";
import { getVaultEntries } from "@/lib/vault";
import { buildPageMetadata } from "@/lib/site";

export const metadata = buildPageMetadata({
  title: "Vault",
  description: "A searchable founder knowledge vault spanning writing, worldview, and source material.",
  path: "/vault",
});

export default function VaultPage() {
  const entries = getVaultEntries();

  return <VaultWorkspace entries={entries} />;
}
