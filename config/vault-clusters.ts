export type VaultCluster = {
  label: string;
  icon: string;
  keywords: string[];
};

export const vaultClusters: VaultCluster[] = [
  {
    label: "Writing Craft",
    icon: "✎",
    keywords: ["writing", "style", "prose", "essay", "narrative", "story"],
  },
  {
    label: "Strategy",
    icon: "◈",
    keywords: ["strategy", "growth", "pricing", "market", "competition", "bootstrapping", "PMF"],
  },
  {
    label: "Product Building",
    icon: "⬡",
    keywords: ["product", "MVP", "hiring", "startup", "SaaS", "build"],
  },
  {
    label: "Founder Stories",
    icon: "○",
    keywords: ["founder", "entrepreneurship", "indie", "solo", "acquisition", "exit"],
  },
];
