"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { ArrowUpRight, ChevronDown, ChevronRight } from "lucide-react";
import Fuse from "fuse.js";
import { SiteShell } from "@/components/site-shell";
import type { VaultEntry } from "@/lib/vault";
import { vaultPicks } from "@/config/vault-picks";
import { vaultClusters } from "@/config/vault-clusters";

type VaultWorkspaceProps = {
  entries: VaultEntry[];
};

const POPULAR_CHIPS = ["PMF", "writing", "growth", "pricing", "bootstrapping", "hiring", "MVP"];
const AUTHOR_CHIPS = ["Paul Graham", "Shaan Puri", "Jason Fried", "Tim Urban", "Jason Cohen", "David Perell"];

const PLACEHOLDER_SUGGESTIONS = [
  "Try: product-market fit",
  "Try: writing style",
  "Try: startup pricing",
  "Try: Tim Urban",
  "Try: bootstrapping",
];

function useRotatingPlaceholder(suggestions: string[], active: boolean, intervalMs = 3000) {
  const [index, setIndex] = useState(0);
  useEffect(() => {
    if (!active) return;
    const id = setInterval(() => setIndex((i) => (i + 1) % suggestions.length), intervalMs);
    return () => clearInterval(id);
  }, [active, suggestions.length, intervalMs]);
  return suggestions[index] ?? suggestions[0] ?? "";
}

function getTopAuthors(entries: VaultEntry[]) {
  const counts = new Map<string, number>();
  for (const entry of entries) {
    const author = entry.authorLabel;
    if (author && author !== "Unknown") {
      counts.set(author, (counts.get(author) ?? 0) + 1);
    }
  }
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 12)
    .map(([author, count]) => ({ author, count }));
}

function getTopLevelFolders(entries: VaultEntry[]) {
  const counts = new Map<string, number>();
  for (const entry of entries) {
    const top = entry.folderPath.split("/")[0];
    if (top) counts.set(top, (counts.get(top) ?? 0) + 1);
  }
  return [...counts.entries()].sort((a, b) => a[0].localeCompare(b[0]));
}

export function VaultWorkspace({ entries }: VaultWorkspaceProps) {
  const [query, setQuery] = useState("");
  const [activeFolder, setActiveFolder] = useState<string>("");
  const [terminalOpen, setTerminalOpen] = useState(false);

  const isSearching = query.trim().length > 0;
  const placeholder = useRotatingPlaceholder(PLACEHOLDER_SUGGESTIONS, !isSearching);
  const inputRef = useRef<HTMLInputElement>(null);

  const fuse = useMemo(
    () =>
      new Fuse(entries, {
        keys: ["title", "authorLabel", "folderPath", "snippet"],
        threshold: 0.35,
        includeScore: true,
      }),
    [entries],
  );

  const searchResults = useMemo(() => {
    if (!query.trim()) return [];
    return fuse.search(query.trim()).map((r) => r.item);
  }, [fuse, query]);

  const folderFiltered = useMemo(() => {
    if (!activeFolder) return entries;
    return entries.filter((e) => e.folderPath === activeFolder || e.folderPath.startsWith(`${activeFolder}/`));
  }, [entries, activeFolder]);

  const displayEntries = isSearching ? searchResults : folderFiltered;
  const hasResults = displayEntries.length > 0;

  const entryBySlug = useMemo(() => new Map(entries.map((e) => [e.slug, e])), [entries]);

  const pickedEntries = useMemo(
    () =>
      vaultPicks
        .map((pick) => {
          const entry = entryBySlug.get(pick.slug);
          return entry ? { entry, note: pick.note } : null;
        })
        .filter((item): item is NonNullable<typeof item> => item !== null),
    [entryBySlug],
  );

  const topAuthors = useMemo(() => getTopAuthors(entries), [entries]);
  const topFolders = useMemo(() => getTopLevelFolders(entries), [entries]);

  function handleChip(term: string) {
    setQuery(term);
    setActiveFolder("");
    inputRef.current?.focus();
  }

  function handleFolderFilter(folder: string) {
    setActiveFolder(activeFolder === folder ? "" : folder);
    setQuery("");
  }

  const terminalLines = [
    "knowledge vault online",
    `${entries.length} indexed sources loaded`,
    activeFolder ? `scope: ${activeFolder}` : "scope: root",
    query ? `query: ${query}` : "query: idle",
  ];

  const sidebar = useMemo(
    () => (
      <div className="space-y-4">
        <div className="space-y-1">
          <p className="px-1 text-[10px] uppercase tracking-[0.22em] text-white/28">vault/</p>
          <button
            className={`flex w-full items-center rounded-md px-3 py-2 text-left text-[12px] transition ${
              !activeFolder ? "bg-white/[0.06] text-white" : "text-white/42 hover:bg-white/[0.04] hover:text-white/72"
            }`}
            onClick={() => { setActiveFolder(""); setQuery(""); }}
            type="button"
          >
            vault/ ({entries.length})
          </button>
          {topFolders.map(([folder, count]) => (
            <button
              className={`flex w-full items-center rounded-md px-3 py-2 pl-6 text-left text-[12px] transition ${
                activeFolder === folder
                  ? "bg-white/[0.06] text-white"
                  : "text-white/38 hover:bg-white/[0.04] hover:text-white/65"
              }`}
              key={folder}
              onClick={() => handleFolderFilter(folder)}
              type="button"
            >
              {folder}/ ({count})
            </button>
          ))}
        </div>
      </div>
    ),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [activeFolder, entries.length, topFolders],
  );

  return (
    <SiteShell
      activityKey="vault"
      breadcrumbs={[{ label: "andochoa.com", href: "/" }, { label: "vault" }]}
      sidebar={sidebar}
      sidebarTitle="vault"
      statusMeta={`vault · ${entries.length} entries`}
      tabs={[{ active: true, label: "vault" }]}
    >
      <div className="space-y-8">
        <section className="space-y-4">
          <div className="relative">
            <input
              ref={inputRef}
              className="w-full rounded-lg border border-white/14 bg-white/[0.04] px-5 py-4 text-[15px] text-white outline-none placeholder:text-white/28 focus:border-white/24 focus:bg-white/[0.06] transition"
              onChange={(e) => { setQuery(e.target.value); setActiveFolder(""); }}
              placeholder={placeholder}
              type="search"
              value={query}
              aria-label="Search vault"
            />
            {query && (
              <button
                className="absolute right-4 top-1/2 -translate-y-1/2 text-[11px] text-white/36 hover:text-white/60 transition"
                onClick={() => setQuery("")}
                type="button"
              >
                clear
              </button>
            )}
          </div>

          <div className="space-y-2">
            <div className="flex flex-wrap gap-2">
              {POPULAR_CHIPS.map((chip) => (
                <button
                  className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1 text-[12px] text-white/56 transition hover:border-white/20 hover:bg-white/[0.06] hover:text-white"
                  key={chip}
                  onClick={() => handleChip(chip)}
                  type="button"
                >
                  {chip}
                </button>
              ))}
            </div>
            <div className="flex flex-wrap gap-2">
              {AUTHOR_CHIPS.map((author) => (
                <button
                  className="rounded-full border border-white/8 bg-white/[0.02] px-3 py-1 text-[12px] text-white/42 transition hover:border-white/16 hover:bg-white/[0.04] hover:text-white/72"
                  key={author}
                  onClick={() => handleChip(author)}
                  type="button"
                >
                  {author}
                </button>
              ))}
            </div>
          </div>
        </section>

        {isSearching && (
          <section>
            {hasResults ? (
              <div className="space-y-2">
                <p className="text-[10px] uppercase tracking-[0.22em] text-white/28">
                  {displayEntries.length} result{displayEntries.length !== 1 ? "s" : ""} for &ldquo;{query}&rdquo;
                </p>
                <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
                  {displayEntries.slice(0, 20).map((entry) => (
                    <ResultCard key={entry.id} entry={entry} />
                  ))}
                </div>
              </div>
            ) : (
              <NoResults query={query} onChip={handleChip} />
            )}
          </section>
        )}

        {!isSearching && (
          <>
            {pickedEntries.length > 0 && (
              <section className="space-y-3">
                <p className="text-[10px] uppercase tracking-[0.22em] text-white/28">curated picks</p>
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  {pickedEntries.map(({ entry, note }) => (
                    <PickCard key={entry.id} entry={entry} note={note} />
                  ))}
                </div>
              </section>
            )}

            <section className="space-y-3">
              <p className="text-[10px] uppercase tracking-[0.22em] text-white/28">browse by topic</p>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {vaultClusters.map((cluster) => (
                  <button
                    className="rounded-lg border border-dashed border-white/10 bg-white/[0.02] p-4 text-left transition hover:border-white/18 hover:bg-white/[0.04]"
                    key={cluster.label}
                    onClick={() => handleChip(cluster.keywords[0] ?? cluster.label)}
                    type="button"
                  >
                    <span className="text-[18px]">{cluster.icon}</span>
                    <p className="mt-2 text-[13px] text-white">{cluster.label}</p>
                    <p className="mt-1 text-[11px] text-white/38">{cluster.keywords.slice(0, 3).join(", ")}</p>
                  </button>
                ))}
              </div>
            </section>

            <section className="space-y-3">
              <p className="text-[10px] uppercase tracking-[0.22em] text-white/28">authors</p>
              <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-none">
                {topAuthors.map(({ author, count }) => (
                  <button
                    className="shrink-0 rounded-lg border border-dashed border-white/10 bg-white/[0.02] px-4 py-3 text-left transition hover:border-white/18 hover:bg-white/[0.04]"
                    key={author}
                    onClick={() => handleChip(author)}
                    type="button"
                  >
                    <p className="text-[12px] text-white">{author}</p>
                    <p className="mt-1 text-[10px] text-white/36">{count} entries</p>
                  </button>
                ))}
              </div>
            </section>

            {activeFolder && (
              <section className="space-y-2">
                <p className="text-[10px] uppercase tracking-[0.22em] text-white/28">
                  {activeFolder}/ · {folderFiltered.length} entries
                </p>
                <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
                  {folderFiltered.slice(0, 20).map((entry) => (
                    <ResultCard key={entry.id} entry={entry} />
                  ))}
                </div>
              </section>
            )}

            <section className="overflow-hidden rounded-lg border border-dashed border-white/10">
              <button
                className="flex w-full items-center gap-2 border-b border-white/7 bg-white/[0.02] px-4 py-3 text-left"
                onClick={() => setTerminalOpen((o) => !o)}
                type="button"
              >
                <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
                <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
                <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
                <span className="ml-2 text-[10px] text-white/36">power user? use the terminal</span>
                <span className="ml-auto text-white/28">
                  {terminalOpen ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}
                </span>
              </button>
              {terminalOpen && (
                <div className="vault-terminal space-y-2 px-4 py-4 text-[12px] leading-7">
                  {terminalLines.map((line) => (
                    <p key={line}>{line}</p>
                  ))}
                </div>
              )}
            </section>
          </>
        )}
      </div>
    </SiteShell>
  );
}

function ResultCard({ entry }: { entry: VaultEntry }) {
  const year = new Date(entry.publishedAt).getFullYear();

  return (
    <div className="rounded-md border border-dashed border-white/10 bg-white/[0.03] px-4 py-3 transition hover:bg-white/[0.05]">
      <p className="text-[13px] text-white">{entry.title}</p>
      <p className="mt-1 text-[11px] text-white/40">
        {entry.authorLabel} · {entry.folderPath} · {year}
      </p>
      {entry.snippet && (
        <p className="mt-1.5 text-[12px] text-white/28 line-clamp-2">{entry.snippet}</p>
      )}
      {entry.sourceUrl && (
        <Link
          className="mt-2 inline-flex items-center gap-1 text-[11px] text-white/38 transition hover:text-white/70"
          href={entry.sourceUrl}
          rel="noreferrer"
          target="_blank"
        >
          source <ArrowUpRight className="h-3 w-3" />
        </Link>
      )}
    </div>
  );
}

function PickCard({ entry, note }: { entry: VaultEntry; note: string }) {
  return (
    <div className="rounded-lg border border-white/12 bg-white/[0.04] p-4 space-y-3">
      <blockquote className="text-[12px] text-white/60 italic leading-relaxed">
        &ldquo;{note}&rdquo;
      </blockquote>
      <div>
        <p className="text-[13px] text-white">{entry.title}</p>
        <p className="mt-0.5 text-[11px] text-white/36">{entry.authorLabel}</p>
      </div>
      {entry.sourceUrl && (
        <Link
          className="inline-flex items-center gap-1 text-[11px] text-white/38 transition hover:text-white/70"
          href={entry.sourceUrl}
          rel="noreferrer"
          target="_blank"
        >
          open source <ArrowUpRight className="h-3 w-3" />
        </Link>
      )}
    </div>
  );
}

function NoResults({ query, onChip }: { query: string; onChip: (term: string) => void }) {
  return (
    <div className="rounded-lg border border-dashed border-white/10 px-6 py-8 text-center space-y-4">
      <p className="text-[14px] text-white/60">Nothing found for &ldquo;{query}&rdquo;</p>
      <p className="text-[11px] text-white/30">Try one of these instead:</p>
      <div className="flex flex-wrap justify-center gap-2">
        {POPULAR_CHIPS.slice(0, 4).map((chip) => (
          <button
            className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1 text-[12px] text-white/56 transition hover:border-white/20 hover:text-white"
            key={chip}
            onClick={() => onChip(chip)}
            type="button"
          >
            {chip}
          </button>
        ))}
      </div>
    </div>
  );
}
