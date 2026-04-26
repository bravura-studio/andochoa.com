"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { ArrowUpRight } from "lucide-react";
import { SiteShell } from "@/components/site-shell";
import type { VaultEntry } from "@/lib/vault";

type VaultWorkspaceProps = {
  entries: VaultEntry[];
};

type TreeNode = {
  name: string;
  path: string;
  children: TreeNode[];
};

function formatDisplayDate(value: string) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
  }).format(new Date(value));
}

function buildTree(entries: VaultEntry[]) {
  const root: TreeNode = { name: "root", path: "", children: [] };

  for (const entry of entries) {
    const segments = entry.folderPath.split("/").filter(Boolean);
    let pointer = root;
    let currentPath = "";

    for (const segment of segments) {
      currentPath = currentPath ? `${currentPath}/${segment}` : segment;
      let child = pointer.children.find((candidate) => candidate.name === segment);

      if (!child) {
        child = { name: segment, path: currentPath, children: [] };
        pointer.children.push(child);
      }

      pointer = child;
    }
  }

  return root;
}

export function VaultWorkspace({ entries }: VaultWorkspaceProps) {
  const [query, setQuery] = useState("");
  const [activePath, setActivePath] = useState("");
  const [selectedSlug, setSelectedSlug] = useState<string | null>(entries[0]?.slug ?? null);
  const tree = useMemo(() => buildTree(entries), [entries]);
  const [expandedPaths, setExpandedPaths] = useState<string[]>(() => tree.children.map((child) => child.path));

  const filteredEntries = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();

    return entries.filter((entry) => {
      const pathMatches = !activePath || entry.folderPath === activePath || entry.folderPath.startsWith(`${activePath}/`);

      if (!pathMatches) {
        return false;
      }

      if (!normalizedQuery) {
        return true;
      }

      return [entry.title, entry.authorLabel, entry.folderPath, entry.fileName].join(" ").toLowerCase().includes(normalizedQuery);
    });
  }, [activePath, entries, query]);

  const selectedEntry =
    filteredEntries.find((entry) => entry.slug === selectedSlug) ??
    entries.find((entry) => entry.slug === selectedSlug) ??
    filteredEntries[0] ??
    entries[0] ??
    null;

  const terminalLines = [
    "knowledge vault online",
    `${entries.length} indexed sources loaded`,
    activePath ? `scope: ${activePath}` : "scope: root",
    query ? `query: ${query}` : "query: idle",
  ];

  function toggleFolder(path: string) {
    setActivePath((current) => (current === path ? "" : path));
    setExpandedPaths((current) => (current.includes(path) ? current.filter((item) => item !== path) : [...current, path]));
  }

  return (
    <SiteShell
      activityKey="vault"
      breadcrumbs={[{ label: "andochoa.com", href: "/" }, { label: "vault" }]}
      sidebar={
        <div className="space-y-4">
          <input
            className="w-full rounded-md border border-white/8 bg-white/[0.03] px-3 py-2 text-[11px] text-white outline-none placeholder:text-white/22 focus:border-white/14"
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search vault"
            type="search"
            value={query}
          />
          <div className="space-y-1 border-t border-white/7 pt-3">
            {renderTreeWithExpansion(tree, activePath, expandedPaths, toggleFolder)}
          </div>
        </div>
      }
      sidebarTitle="vault"
      statusMeta={`vault · ${filteredEntries.length} entries`}
      tabs={[{ active: true, label: "vault" }]}
    >
      <div className="grid gap-4 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
        <section className="overflow-hidden rounded-lg border border-dashed border-white/12 bg-[#080808]">
          <div className="flex items-center gap-2 border-b border-white/7 bg-white/[0.02] px-4 py-3">
            <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
            <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
            <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
            <span className="ml-auto text-[10px] uppercase tracking-[0.22em] text-white/24">vault terminal</span>
          </div>
          <div className="vault-terminal space-y-2 px-4 py-4 text-[12px] leading-7">
            {terminalLines.map((line) => (
              <p key={line}>{line}</p>
            ))}
            {selectedEntry ? <p className="text-white/42">open: {selectedEntry.fileName}</p> : null}
          </div>
        </section>

        <section className="space-y-3">
          {selectedEntry ? (
            <article className="shell-card p-4">
              <p className="text-[10px] uppercase tracking-[0.24em] text-white/28">{selectedEntry.folderPath}</p>
              <h2 className="mt-2 text-[18px] text-white">{selectedEntry.title}</h2>
              <p className="mt-2 text-[12px] text-white/36">
                {selectedEntry.authorLabel} · {formatDisplayDate(selectedEntry.publishedAt)}
              </p>
              {selectedEntry.sourceUrl ? (
                <Link
                  className="mt-4 inline-flex items-center gap-2 text-[12px] text-white/56 transition hover:text-white"
                  href={selectedEntry.sourceUrl}
                  rel="noreferrer"
                  target="_blank"
                >
                  Open source
                  <ArrowUpRight className="h-4 w-4" />
                </Link>
              ) : null}
            </article>
          ) : null}

          <div className="max-h-[520px] space-y-2 overflow-y-auto pr-1">
            {filteredEntries.map((entry) => (
              <button
                className={`w-full rounded-md border border-dashed px-4 py-3 text-left transition ${
                  entry.slug === selectedEntry?.slug
                    ? "border-white/12 bg-white/[0.06]"
                    : "border-white/10 bg-white/[0.03] hover:bg-white/[0.05]"
                }`}
                key={entry.id}
                onClick={() => setSelectedSlug(entry.slug)}
                type="button"
              >
                <div className="flex items-center gap-3 text-[10px] uppercase tracking-[0.18em] text-white/28">
                  <span>{formatDisplayDate(entry.publishedAt)}</span>
                  <span>{entry.authorLabel}</span>
                </div>
                <p className="mt-2 text-[13px] text-white">{entry.title}</p>
                <p className="mt-1 text-[11px] text-white/40">{entry.relativePath}</p>
              </button>
            ))}
          </div>
        </section>
      </div>
    </SiteShell>
  );
}

function renderTreeWithExpansion(
  node: TreeNode,
  activePath: string,
  expandedPaths: string[],
  onToggle: (path: string) => void,
  depth = 0,
): React.ReactNode {
  return node.children
    .sort((left, right) => left.path.localeCompare(right.path))
    .map((child) => {
      const active = activePath === child.path;
      const expanded = expandedPaths.includes(child.path) || activePath.startsWith(`${child.path}/`);

      return (
        <div key={child.path}>
          <button
            className={`flex w-full items-center rounded-md px-3 py-2 text-left text-[12px] transition ${
              active ? "bg-white/[0.06] text-white" : "text-white/38 hover:bg-white/[0.04] hover:text-white/72"
            }`}
            onClick={() => onToggle(child.path)}
            style={{ paddingLeft: `${12 + depth * 12}px` }}
            type="button"
          >
            {child.children.length ? (expanded ? "▾" : "▸") : "•"} {child.name}/
          </button>
          {child.children.length && expanded ? renderTreeWithExpansion(child, activePath, expandedPaths, onToggle, depth + 1) : null}
        </div>
      );
    });
}
