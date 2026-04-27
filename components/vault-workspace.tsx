"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ArrowUpRight, ChevronUp, X } from "lucide-react";
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

function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

function getTopAuthors(entries: VaultEntry[]) {
  const counts = new Map<string, number>();
  for (const entry of entries) {
    const a = entry.authorLabel;
    if (a && a !== "Unknown") counts.set(a, (counts.get(a) ?? 0) + 1);
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

function getDomain(url: string | null): string | null {
  if (!url) return null;
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return null;
  }
}

function getUniqueAuthorCount(entries: VaultEntry[]): number {
  const s = new Set<string>();
  for (const e of entries) {
    if (e.authorLabel && e.authorLabel !== "Unknown") s.add(e.authorLabel);
  }
  return s.size;
}

export function VaultWorkspace({ entries }: VaultWorkspaceProps) {
  const [rawQuery, setRawQuery] = useState("");
  const [activeFolder, setActiveFolder] = useState<string>("");
  const [activeCluster, setActiveCluster] = useState<string>("");
  const [activeAuthor, setActiveAuthor] = useState<string>("");
  const [showBackToTop, setShowBackToTop] = useState(false);
  const [mode, setMode] = useState<"browse" | "focus">("browse");

  const query = useDebounce(rawQuery, 300);
  const isSearching = query.trim().length > 0;
  const hasFilter = isSearching || !!activeCluster || !!activeAuthor || !!activeFolder;
  const isFocus = mode === "focus";

  // Active filter label for display in breadcrumbs, tabs, status bar
  const activeFilterLabel = isSearching
    ? query.trim()
    : activeCluster || activeAuthor || activeFolder || "";

  const placeholder = useRotatingPlaceholder(PLACEHOLDER_SUGGESTIONS, !isSearching && !isFocus);
  const inputRef = useRef<HTMLInputElement>(null);
  const clustersRef = useRef<HTMLElement>(null);

  // Back-to-top: appear after user scrolls past clusters section
  useEffect(() => {
    const scrollEl = document.querySelector(".shell-content-scroll") ?? window;
    const handleScroll = () => {
      const el = clustersRef.current;
      if (!el) return;
      setShowBackToTop(el.getBoundingClientRect().bottom < 0);
    };
    scrollEl.addEventListener("scroll", handleScroll, { passive: true });
    return () => scrollEl.removeEventListener("scroll", handleScroll);
  }, []);

  // Escape key: return to browse mode
  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape" && mode === "focus") {
        clearFilters();
      }
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode]);

  const fuse = useMemo(
    () =>
      new Fuse(entries, {
        keys: ["title", "authorLabel", "folderPath", "snippet"],
        threshold: 0.35,
        includeScore: true,
      }),
    [entries],
  );

  const displayEntries = useMemo(() => {
    if (isSearching) return fuse.search(query.trim()).map((r) => r.item);
    if (activeAuthor) return entries.filter((e) => e.authorLabel === activeAuthor);
    if (activeCluster) {
      const cluster = vaultClusters.find((c) => c.label === activeCluster);
      if (!cluster) return [];
      const kws = cluster.keywords.map((k) => k.toLowerCase());
      return entries.filter((e) => {
        const text = `${e.title} ${e.folderPath} ${e.snippet} ${e.authorLabel}`.toLowerCase();
        return kws.some((kw) => text.includes(kw));
      });
    }
    if (activeFolder) {
      return entries.filter(
        (e) => e.folderPath === activeFolder || e.folderPath.startsWith(`${activeFolder}/`),
      );
    }
    return [];
  }, [fuse, query, isSearching, activeAuthor, activeCluster, activeFolder, entries]);

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
  const uniqueAuthorCount = useMemo(() => getUniqueAuthorCount(entries), [entries]);
  const collectionCount = topFolders.length;

  // Top 3 entries per author for spotlight preview
  const authorTopEntries = useMemo(() => {
    const map = new Map<string, VaultEntry[]>();
    for (const { author } of topAuthors) {
      map.set(author, entries.filter((e) => e.authorLabel === author).slice(0, 3));
    }
    return map;
  }, [topAuthors, entries]);

  // Cluster entry counts for sidebar display
  const clusterCounts = useMemo(() => {
    const map = new Map<string, number>();
    for (const cluster of vaultClusters) {
      const kws = cluster.keywords.map((k) => k.toLowerCase());
      const count = entries.filter((e) => {
        const text = `${e.title} ${e.folderPath} ${e.snippet} ${e.authorLabel}`.toLowerCase();
        return kws.some((kw) => text.includes(kw));
      }).length;
      map.set(cluster.label, count);
    }
    return map;
  }, [entries]);

  // Sidebar section collapse state
  const [topicsExpanded, setTopicsExpanded] = useState(true);
  const [authorsExpanded, setAuthorsExpanded] = useState(true);
  const [foldersExpanded, setFoldersExpanded] = useState(false);

  const scrollToTop = useCallback(() => {
    requestAnimationFrame(() => {
      (document.querySelector(".shell-content-scroll") as HTMLElement | null)?.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    });
  }, []);

  function clearFilters() {
    setRawQuery("");
    setActiveCluster("");
    setActiveAuthor("");
    setActiveFolder("");
    setMode("browse");
  }

  function handleChip(term: string) {
    setRawQuery(term);
    setActiveCluster("");
    setActiveAuthor("");
    setActiveFolder("");
    setMode("focus");
    inputRef.current?.focus();
    scrollToTop();
  }

  function handleFolderFilter(folder: string) {
    const next = activeFolder === folder ? "" : folder;
    setActiveFolder(next);
    setRawQuery("");
    setActiveCluster("");
    setActiveAuthor("");
    if (next) {
      setMode("focus");
      scrollToTop();
    } else {
      setMode("browse");
    }
  }

  function handleCluster(label: string) {
    const next = activeCluster === label ? "" : label;
    setActiveCluster(next);
    setRawQuery("");
    setActiveAuthor("");
    setActiveFolder("");
    if (next) {
      setMode("focus");
      scrollToTop();
    } else {
      setMode("browse");
    }
  }

  function handleAuthor(author: string) {
    const next = activeAuthor === author ? "" : author;
    setActiveAuthor(next);
    setRawQuery("");
    setActiveCluster("");
    setActiveFolder("");
    if (next) {
      setMode("focus");
      scrollToTop();
    } else {
      setMode("browse");
    }
  }

  function handleBackToTop() {
    (document.querySelector(".shell-content-scroll") as HTMLElement | null)?.scrollTo({
      top: 0,
      behavior: "smooth",
    });
    inputRef.current?.focus();
  }

  // Dynamic SiteShell props based on mode
  const breadcrumbs = isFocus && activeFilterLabel
    ? [
        { label: "andochoa.com", href: "/" },
        { label: "vault", href: "/vault" },
        { label: activeFilterLabel },
      ]
    : [{ label: "andochoa.com", href: "/" }, { label: "vault" }];

  const tabs = isFocus && activeFilterLabel
    ? [{ active: true, label: `vault/${activeFilterLabel}` }]
    : [{ active: true, label: "vault" }];

  const statusMeta = isFocus && hasFilter
    ? activeFilterLabel
      ? `${displayEntries.length} result${displayEntries.length !== 1 ? "s" : ""} for '${activeFilterLabel}'`
      : `${displayEntries.length} result${displayEntries.length !== 1 ? "s" : ""}`
    : `vault · ${entries.length} sources`;

  // Active sidebar item — only one at a time; cleared by search or browse mode
  const sidebarActiveCluster = isSearching || !isFocus ? "" : activeCluster;
  const sidebarActiveAuthor = isSearching || !isFocus ? "" : activeAuthor;
  const sidebarActiveFolder = isSearching || !isFocus ? "" : activeFolder;

  const sidebar = useMemo(
    () => (
      <div className="space-y-4">
        {/* vault root */}
        <div className="space-y-0.5">
          <p className="px-3 py-1 text-[9px] uppercase tracking-[0.2em] text-white/22">
            vault/ ({entries.length})
          </p>
        </div>

        {/* TOPICS */}
        <div className="space-y-0.5">
          <button
            className="flex w-full items-center gap-1 px-3 py-1 text-[9px] uppercase tracking-[0.2em] text-white/22 transition hover:text-white/40"
            onClick={() => setTopicsExpanded((v) => !v)}
            type="button"
          >
            {topicsExpanded ? "▾" : "▸"} TOPICS
          </button>
          {topicsExpanded && vaultClusters.map((cluster) => {
            const isActive = sidebarActiveCluster === cluster.label;
            const count = clusterCounts.get(cluster.label) ?? 0;
            return (
              <button
                className={`flex w-full items-center justify-between border-l-2 py-1.5 pl-3 pr-3 text-left text-[12px] transition ${
                  isActive
                    ? "border-white/80 bg-white/[0.06] text-white"
                    : "border-transparent text-white/42 hover:bg-white/[0.04] hover:text-white/72"
                }`}
                key={cluster.label}
                onClick={() => handleCluster(cluster.label)}
                type="button"
              >
                <span>{cluster.label}</span>
                <span className="text-[10px] text-white/28">{count}</span>
              </button>
            );
          })}
        </div>

        {/* AUTHORS */}
        <div className="space-y-0.5">
          <button
            className="flex w-full items-center gap-1 px-3 py-1 text-[9px] uppercase tracking-[0.2em] text-white/22 transition hover:text-white/40"
            onClick={() => setAuthorsExpanded((v) => !v)}
            type="button"
          >
            {authorsExpanded ? "▾" : "▸"} AUTHORS
          </button>
          {authorsExpanded && topAuthors.map(({ author, count }) => {
            const isActive = sidebarActiveAuthor === author;
            return (
              <button
                className={`flex w-full items-center justify-between border-l-2 py-1.5 pl-3 pr-3 text-left text-[12px] transition ${
                  isActive
                    ? "border-white/80 bg-white/[0.06] text-white"
                    : "border-transparent text-white/42 hover:bg-white/[0.04] hover:text-white/72"
                }`}
                key={author}
                onClick={() => handleAuthor(author)}
                type="button"
              >
                <span className="truncate">{author}</span>
                <span className="ml-2 shrink-0 text-[10px] text-white/28">{count}</span>
              </button>
            );
          })}
        </div>

        {/* FOLDERS */}
        <div className="space-y-0.5">
          <button
            className="flex w-full items-center gap-1 px-3 py-1 text-[9px] uppercase tracking-[0.2em] text-white/22 transition hover:text-white/40"
            onClick={() => setFoldersExpanded((v) => !v)}
            type="button"
          >
            {foldersExpanded ? "▾" : "▸"} FOLDERS
          </button>
          {foldersExpanded && topFolders.map(([folder, count]) => {
            const isActive = sidebarActiveFolder === folder;
            return (
              <button
                className={`flex w-full items-center justify-between border-l-2 py-1.5 pl-3 pr-3 text-left text-[12px] transition ${
                  isActive
                    ? "border-white/80 bg-white/[0.06] text-white"
                    : "border-transparent text-white/42 hover:bg-white/[0.04] hover:text-white/72"
                }`}
                key={folder}
                onClick={() => handleFolderFilter(folder)}
                type="button"
              >
                <span>{folder}/</span>
                <span className="text-[10px] text-white/28">{count}</span>
              </button>
            );
          })}
        </div>
      </div>
    ),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [
      sidebarActiveCluster, sidebarActiveAuthor, sidebarActiveFolder,
      entries.length, topFolders, topAuthors, clusterCounts,
      topicsExpanded, authorsExpanded, foldersExpanded,
    ],
  );

  return (
    <SiteShell
      activityKey="vault"
      breadcrumbs={breadcrumbs}
      sidebar={sidebar}
      sidebarTitle="vault"
      statusMeta={statusMeta}
      tabs={tabs}
    >
      <div className="space-y-8">
        {/* 1. Search bar — sticky at top */}
        <section className="space-y-4">
          <div className="sticky top-0 z-10 -mx-4 px-4 pb-3 pt-1 sm:-mx-6 sm:px-6 bg-[#0a0a0a]/95 backdrop-blur-sm">
            <div className="flex items-center gap-3">
              <div className="relative flex-1">
                <input
                  ref={inputRef}
                  aria-label="Search vault"
                  className="w-full rounded-lg border border-white/14 bg-white/[0.04] px-5 py-4 text-[15px] text-white outline-none placeholder:text-white/28 focus:border-white/24 focus:bg-white/[0.06] transition"
                  onChange={(e) => {
                    setRawQuery(e.target.value);
                    setActiveCluster("");
                    setActiveAuthor("");
                    setActiveFolder("");
                    setMode(e.target.value ? "focus" : "browse");
                  }}
                  placeholder={placeholder}
                  type="search"
                  value={rawQuery}
                />
                {rawQuery && (
                  <button
                    className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-1 text-[11px] text-white/36 hover:text-white/60 transition"
                    onClick={clearFilters}
                    type="button"
                  >
                    <X className="h-3 w-3" />
                    clear
                  </button>
                )}
              </div>
              {/* Back to vault button — only in focus mode */}
              {isFocus && (
                <button
                  className="shrink-0 flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-4 text-[11px] text-white/40 transition hover:border-white/20 hover:text-white/68"
                  onClick={clearFilters}
                  type="button"
                >
                  <X className="h-3 w-3" />
                  vault
                </button>
              )}
            </div>

            {/* Active non-text filter pill */}
            {isFocus && !isSearching && hasFilter && (
              <div className="mt-2 flex items-center gap-2">
                <span className="text-[11px] text-white/28">filtered by</span>
                <span className="rounded-full border border-white/18 bg-white/[0.05] px-2.5 py-0.5 text-[11px] text-white/64">
                  {activeCluster || activeAuthor || activeFolder}
                </span>
                <button
                  className="flex items-center gap-1 text-[11px] text-white/28 hover:text-white/50 transition"
                  onClick={clearFilters}
                  type="button"
                >
                  <X className="h-2.5 w-2.5" />
                  clear
                </button>
              </div>
            )}
          </div>

          {/* Chips — hidden in focus mode */}
          <div
            style={{
              maxHeight: isFocus ? 0 : 200,
              opacity: isFocus ? 0 : 1,
              transform: isFocus ? "translateY(-10px)" : "translateY(0)",
              overflow: "hidden",
              transition: "max-height 200ms ease, opacity 200ms ease, transform 200ms ease",
              pointerEvents: isFocus ? "none" : undefined,
            }}
          >
            <div className="space-y-2">
              <div className="flex flex-wrap gap-2">
                {POPULAR_CHIPS.map((chip) => (
                  <button
                    className={`rounded-full border px-3 py-1 text-[12px] transition ${
                      rawQuery === chip
                        ? "border-white/30 bg-white/[0.10] text-white"
                        : "border-white/10 bg-white/[0.03] text-white/56 hover:border-white/20 hover:bg-white/[0.06] hover:text-white"
                    }`}
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
                    className={`rounded-full border px-3 py-1 text-[12px] transition ${
                      rawQuery === author
                        ? "border-white/20 bg-white/[0.07] text-white/80"
                        : "border-white/8 bg-white/[0.02] text-white/42 hover:border-white/16 hover:bg-white/[0.04] hover:text-white/72"
                    }`}
                    key={author}
                    onClick={() => handleChip(author)}
                    type="button"
                  >
                    {author}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Browse sections — fade out in focus mode */}
        <div
          style={{
            maxHeight: isFocus ? 0 : 10000,
            opacity: isFocus ? 0 : 1,
            transform: isFocus ? "translateY(-10px)" : "translateY(0)",
            overflow: "hidden",
            transition: "max-height 200ms ease, opacity 200ms ease, transform 200ms ease",
            pointerEvents: isFocus ? "none" : undefined,
          }}
        >
          <div className="space-y-8">
            {/* Stats bar */}
            <section>
              <p className="text-[11px] text-white/28 tracking-wide">
                {entries.length} sources · {uniqueAuthorCount} authors · {collectionCount} collections ·
                curated since 2025
              </p>
            </section>

            {/* Curated picks — horizontal scroll on mobile */}
            {pickedEntries.length > 0 && (
              <section className="space-y-3">
                <p className="text-[10px] uppercase tracking-[0.22em] text-white/28">curated picks</p>
                <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-none sm:grid sm:grid-cols-2 lg:grid-cols-3">
                  {pickedEntries.map(({ entry, note }) => (
                    <PickCard key={entry.id} entry={entry} note={note} />
                  ))}
                </div>
              </section>
            )}

            {/* Cluster cards with active state */}
            <section className="space-y-3" ref={clustersRef}>
              <p className="text-[10px] uppercase tracking-[0.22em] text-white/28">browse by topic</p>
              <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
                {vaultClusters.map((cluster) => (
                  <button
                    className={`rounded-lg border p-4 text-left transition ${
                      activeCluster === cluster.label
                        ? "border-white/28 bg-white/[0.07]"
                        : "border-dashed border-white/10 bg-white/[0.02] hover:border-white/18 hover:bg-white/[0.04]"
                    }`}
                    key={cluster.label}
                    onClick={() => handleCluster(cluster.label)}
                    type="button"
                  >
                    <span className="text-[18px]">{cluster.icon}</span>
                    <p className="mt-2 text-[13px] text-white">{cluster.label}</p>
                    <p className="mt-1 text-[11px] text-white/38">{cluster.keywords.slice(0, 3).join(", ")}</p>
                  </button>
                ))}
              </div>
            </section>

            {/* Author spotlight — interactive, horizontal scroll */}
            <section className="space-y-3">
              <p className="text-[10px] uppercase tracking-[0.22em] text-white/28">authors</p>
              <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-none">
                {topAuthors.map(({ author, count }) => {
                  const preview = authorTopEntries.get(author) ?? [];
                  const isActive = activeAuthor === author;
                  return (
                    <button
                      className={`shrink-0 min-w-[140px] max-w-[180px] rounded-lg border p-4 text-left transition ${
                        isActive
                          ? "border-white/28 bg-white/[0.07]"
                          : "border-dashed border-white/10 bg-white/[0.02] hover:border-white/18 hover:bg-white/[0.04]"
                      }`}
                      key={author}
                      onClick={() => handleAuthor(author)}
                      type="button"
                    >
                      <div className="flex items-center gap-2">
                        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-white/[0.08] text-[11px] text-white/60 font-mono">
                          {author[0]?.toUpperCase()}
                        </div>
                        <span className="rounded px-1.5 py-0.5 text-[10px] text-white/36 border border-white/8 bg-white/[0.03]">
                          {count}
                        </span>
                      </div>
                      <p className="mt-2 text-[12px] text-white leading-tight">{author}</p>
                      {isActive && preview.length > 0 && (
                        <div className="mt-3 space-y-1.5 border-t border-white/8 pt-2">
                          {preview.map((e) => (
                            <div key={e.id} className="space-y-0.5">
                              <p className="text-[10px] text-white/60 leading-snug line-clamp-2">{e.title}</p>
                              {getDomain(e.sourceUrl) && (
                                <p className="text-[9px] text-white/28 font-mono">{getDomain(e.sourceUrl)}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            </section>
          </div>
        </div>

        {/* Results — fade in on focus mode, always in DOM */}
        <div
          style={{
            opacity: isFocus ? 1 : 0,
            transform: isFocus ? "translateY(0)" : "translateY(10px)",
            transition: "opacity 250ms ease, transform 250ms ease",
            pointerEvents: isFocus ? undefined : "none",
          }}
        >
          {hasFilter ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between gap-4">
                <p className="text-[10px] uppercase tracking-[0.22em] text-white/28">
                  {isSearching
                    ? hasResults
                      ? `${displayEntries.length} result${displayEntries.length !== 1 ? "s" : ""} for "${query}"`
                      : `no results for "${query}"`
                    : activeAuthor
                      ? `${displayEntries.length} entr${displayEntries.length !== 1 ? "ies" : "y"} by ${activeAuthor}`
                      : `${displayEntries.length} result${displayEntries.length !== 1 ? "s" : ""}`}
                </p>
              </div>
              {hasResults ? (
                <div className="space-y-2 animate-in fade-in duration-200">
                  {displayEntries.slice(0, 40).map((entry) => (
                    <ResultCard key={entry.id} entry={entry} />
                  ))}
                </div>
              ) : (
                <NoResults query={query} onChip={handleChip} />
              )}
            </div>
          ) : null}
        </div>
      </div>

      {/* Back to top floating button */}
      {showBackToTop && (
        <button
          className="fixed bottom-8 right-8 z-50 flex items-center gap-1.5 rounded-md border border-white/14 bg-[#111111] px-3 py-2 text-[11px] text-white/50 shadow-lg transition hover:border-white/24 hover:text-white/80"
          onClick={handleBackToTop}
          type="button"
        >
          <ChevronUp className="h-3.5 w-3.5" />
          top
        </button>
      )}
    </SiteShell>
  );
}

function ResultCard({ entry }: { entry: VaultEntry }) {
  const year = new Date(entry.publishedAt).getFullYear();
  const domain = getDomain(entry.sourceUrl);

  const inner = (
    <div className="group rounded-md border border-dashed border-white/10 bg-white/[0.03] px-4 py-3 transition hover:border-white/18 hover:bg-white/[0.05] hover:-translate-y-px">
      <div className="flex items-start justify-between gap-3">
        <p className="text-[13px] font-bold text-white leading-snug">{entry.title}</p>
        {domain && (
          <span className="mt-0.5 shrink-0 rounded px-1.5 py-0.5 text-[10px] text-white/28 border border-white/8 bg-white/[0.03] font-mono">
            {domain}
          </span>
        )}
      </div>
      <div className="mt-1 flex items-center justify-between gap-2">
        <p className="text-[11px] text-white/40">{entry.authorLabel}</p>
        <p className="text-[11px] text-white/28">{year}</p>
      </div>
      {entry.snippet && (
        <p className="mt-1.5 text-[12px] text-white/28 line-clamp-2">{entry.snippet}</p>
      )}
    </div>
  );

  if (entry.sourceUrl) {
    return (
      <Link href={entry.sourceUrl} rel="noreferrer" target="_blank" className="block">
        {inner}
      </Link>
    );
  }
  return inner;
}

function PickCard({ entry, note }: { entry: VaultEntry; note: string }) {
  const inner = (
    <div className="flex h-full min-w-[220px] flex-col rounded-lg border border-white/12 bg-white/[0.04] p-4 sm:min-w-0">
      <blockquote className="flex-1 text-[12px] text-white/60 italic leading-relaxed">
        &ldquo;{note}&rdquo;
      </blockquote>
      <div className="mt-3">
        <p className="text-[13px] text-white">{entry.title}</p>
        <p className="mt-0.5 text-[11px] text-white/36">{entry.authorLabel}</p>
      </div>
      {entry.sourceUrl && (
        <span className="mt-2 inline-flex items-center gap-1 text-[11px] text-white/38">
          open source <ArrowUpRight className="h-3 w-3" />
        </span>
      )}
    </div>
  );

  if (entry.sourceUrl) {
    return (
      <Link href={entry.sourceUrl} rel="noreferrer" target="_blank" className="block transition hover:opacity-80">
        {inner}
      </Link>
    );
  }
  return inner;
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
