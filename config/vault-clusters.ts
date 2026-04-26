export type VaultCluster = {
  label: string;
  icon: string;
  keywords: string[];
  folderPaths: string[];
};

export const vaultClusters: VaultCluster[] = [
  {
    label: "Writing Craft",
    icon: "✎",
    keywords: ["writing", "style", "prose", "essay", "narrative", "story"],
    folderPaths: ["great-writing"],
  },
  {
    label: "Strategy",
    icon: "◈",
    keywords: ["strategy", "growth", "pricing", "market", "competition", "bootstrapping", "PMF"],
    folderPaths: ["world-view"],
  },
  {
    label: "Product Building",
    icon: "⬡",
    keywords: ["product", "MVP", "hiring", "startup", "SaaS", "build"],
    folderPaths: ["world-view"],
  },
  {
    label: "Founder Stories",
    icon: "○",
    keywords: ["founder", "entrepreneurship", "indie", "solo", "acquisition", "exit"],
    folderPaths: ["great-writing/founder-stories", "world-view"],
  },
];
