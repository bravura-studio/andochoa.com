"use client";

import { useDeferredValue, useEffect, useMemo, useRef, useState, startTransition } from "react";
import Fuse from "fuse.js";
import Link from "next/link";
import { ArrowUpRight, Command, Search } from "lucide-react";
import type { VaultEntry } from "@/lib/vault";

type VaultWorkspaceProps = {
  entries: VaultEntry[];
};

type TerminalLine = {
  id: string;
  kind: "command" | "output";
  text: string;
  displayText: string;
  prompt?: string;
  isTyping: boolean;
};

const PROMPT = "ochoa@vault:~$";
const TOPIC_FILTERS = ["all", "great-writing", "world-view"] as const;

function formatDisplayDate(value: string) {
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "2-digit",
    year: "numeric",
  }).format(new Date(value));
}

function normalizePath(value: string) {
  return value
    .replace(/^~\//, "")
    .replace(/^\/+/, "")
    .replace(/\/+/g, "/")
    .replace(/\/$/, "");
}

function createTerminalTree(entries: VaultEntry[]) {
  const tree = new Map<string, { dirs: Set<string>; files: VaultEntry[] }>();

  function getNode(pathname: string) {
    if (!tree.has(pathname)) {
      tree.set(pathname, { dirs: new Set<string>(), files: [] });
    }

    return tree.get(pathname)!;
  }

  for (const entry of entries) {
    const segments = entry.folderPath.split("/").filter(Boolean);
    let currentPath = "";

    getNode(currentPath);

    for (const segment of segments) {
      const parent = getNode(currentPath);
      parent.dirs.add(segment);
      currentPath = currentPath ? `${currentPath}/${segment}` : segment;
      getNode(currentPath);
    }

    getNode(entry.folderPath).files.push(entry);
  }

  return tree;
}

function createInitialTerminalLines(totalEntries: number): TerminalLine[] {
  return [
    {
      id: "boot-1",
      kind: "output",
      text: "knowledge vault online",
      displayText: "knowledge vault online",
      isTyping: false,
    },
    {
      id: "boot-2",
      kind: "output",
      text: `${totalEntries} indexed sources loaded`,
      displayText: `${totalEntries} indexed sources loaded`,
      isTyping: false,
    },
    {
      id: "boot-3",
      kind: "output",
      text: "type `help` for commands",
      displayText: "type `help` for commands",
      isTyping: false,
    },
  ];
}

function resolveOpenTarget(entries: VaultEntry[], query: string): { entry: VaultEntry } | { error: string } {
  const normalized = query.trim().toLowerCase();

  if (!normalized) {
    return { error: "usage: open <name>" };
  }

  const exact =
    entries.find((entry) => entry.fileName.toLowerCase() === normalized) ??
    entries.find((entry) => entry.slug.toLowerCase() === normalized) ??
    entries.find((entry) => entry.title.toLowerCase() === normalized);

  if (exact) {
    return { entry: exact };
  }

  const matches = entries.filter((entry) => {
    const haystack = [entry.fileName, entry.slug, entry.title].join(" ").toLowerCase();
    return haystack.includes(normalized);
  });

  if (matches.length === 1) {
    return { entry: matches[0] };
  }

  if (matches.length > 1) {
    return {
      error: `open is ambiguous: ${matches
        .slice(0, 3)
        .map((entry) => entry.fileName)
        .join(", ")}${matches.length > 3 ? " ..." : ""}`,
    };
  }

  return { error: `no source named "${query}"` };
}

export function VaultWorkspace({ entries }: VaultWorkspaceProps) {
  const [query, setQuery] = useState("");
  const [activeTopic, setActiveTopic] = useState<(typeof TOPIC_FILTERS)[number]>("all");
  const [selectedSlug, setSelectedSlug] = useState<string | null>(entries[0]?.slug ?? null);
  const [terminalInput, setTerminalInput] = useState("");
  const [terminalLines, setTerminalLines] = useState<TerminalLine[]>(() => createInitialTerminalLines(entries.length));
  const [typingQueue, setTypingQueue] = useState<string[]>([]);

  const deferredQuery = useDeferredValue(query);
  const terminalViewportRef = useRef<HTMLDivElement | null>(null);
  const terminalInputRef = useRef<HTMLInputElement | null>(null);
  const terminalTree = useMemo(() => createTerminalTree(entries), [entries]);
  const topicEntries = useMemo(
    () => (activeTopic === "all" ? entries : entries.filter((entry) => entry.topic === activeTopic)),
    [activeTopic, entries],
  );
  const fuse = useMemo(
    () =>
      new Fuse(topicEntries, {
        includeScore: true,
        ignoreLocation: true,
        threshold: 0.34,
        keys: ["title", "authorLabel", "folderPath", "fileName", "relativePath"],
      }),
    [topicEntries],
  );

  const filteredEntries = useMemo(() => {
    const normalizedQuery = deferredQuery.trim().toLowerCase();

    if (!normalizedQuery) {
      return topicEntries;
    }

    return fuse.search(normalizedQuery).map((result) => result.item);
  }, [deferredQuery, fuse, topicEntries]);

  const selectedEntry =
    filteredEntries.find((entry) => entry.slug === selectedSlug) ??
    entries.find((entry) => entry.slug === selectedSlug) ??
    filteredEntries[0] ??
    entries[0] ??
    null;

  useEffect(() => {
    if (!selectedEntry && filteredEntries[0]) {
      startTransition(() => setSelectedSlug(filteredEntries[0]?.slug ?? null));
      return;
    }

    if (selectedEntry && !filteredEntries.some((entry) => entry.slug === selectedEntry.slug) && filteredEntries[0]) {
      startTransition(() => setSelectedSlug(filteredEntries[0]?.slug ?? null));
    }
  }, [filteredEntries, selectedEntry]);

  useEffect(() => {
    const activeLineId = typingQueue[0];

    if (!activeLineId) {
      return;
    }

    const activeLine = terminalLines.find((line) => line.id === activeLineId);

    if (!activeLine) {
      setTypingQueue((current) => current.slice(1));
      return;
    }

    if (activeLine.displayText.length >= activeLine.text.length) {
      setTerminalLines((current) =>
        current.map((line) => (line.id === activeLineId ? { ...line, isTyping: false } : line)),
      );
      setTypingQueue((current) => current.slice(1));
      return;
    }

    const timer = window.setTimeout(() => {
      setTerminalLines((current) =>
        current.map((line) =>
          line.id === activeLineId
            ? {
                ...line,
                displayText: line.text.slice(0, Math.min(line.text.length, line.displayText.length + 3)),
              }
            : line,
        ),
      );
    }, 12);

    return () => window.clearTimeout(timer);
  }, [terminalLines, typingQueue]);

  useEffect(() => {
    terminalViewportRef.current?.scrollTo({
      top: terminalViewportRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [terminalLines]);

  function appendOutput(lines: string[]) {
    const nextLines = lines.map((text, index) => ({
      id: `output-${Date.now()}-${index}`,
      kind: "output" as const,
      text,
      displayText: "",
      isTyping: true,
    }));

    setTerminalLines((current) => [...current, ...nextLines]);
    setTypingQueue((current) => [...current, ...nextLines.map((line) => line.id)]);
  }

  function handleCommandSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const rawInput = terminalInput.trim();

    if (!rawInput) {
      return;
    }

    const commandLine: TerminalLine = {
      id: `command-${Date.now()}`,
      kind: "command",
      prompt: PROMPT,
      text: rawInput,
      displayText: rawInput,
      isTyping: false,
    };

    setTerminalLines((current) => [...current, commandLine]);
    setTerminalInput("");

    const [command, ...rest] = rawInput.split(" ");
    const argument = rest.join(" ").trim();

    if (command === "clear") {
      setTypingQueue([]);
      setTerminalLines(createInitialTerminalLines(entries.length));
      return;
    }

    if (command === "help") {
      appendOutput([
        "ls [path]    list directories or indexed files",
        "open <name>  open a source URL in a new tab",
        "find <term>  search titles, authors, and folders",
        "clear        reset terminal output",
      ]);
      return;
    }

    if (command === "ls") {
      const requestedPath = normalizePath(argument);
      const node = terminalTree.get(requestedPath);

      if (!node) {
        appendOutput([`ls: cannot access '${argument || "."}'`]);
        return;
      }

      const directoryEntries = Array.from(node.dirs)
        .sort((left, right) => left.localeCompare(right))
        .map((name) => `${name}/`);
      const fileEntries = [...node.files]
        .sort((left, right) => left.title.localeCompare(right.title))
        .map((entry) => entry.fileName);

      appendOutput([(directoryEntries.length || fileEntries.length ? [...directoryEntries, ...fileEntries] : ["."]).join("  ")]);
      return;
    }

    if (command === "find") {
      const normalized = argument.toLowerCase();

      if (!normalized) {
        appendOutput(["usage: find <keyword>"]);
        return;
      }

      const matches = entries.filter((entry) =>
        [entry.title, entry.authorLabel, entry.folderPath, entry.fileName].join(" ").toLowerCase().includes(normalized),
      );

      if (!matches.length) {
        appendOutput([`no matches for "${argument}"`]);
        return;
      }

      appendOutput([
        `${matches.length} match${matches.length === 1 ? "" : "es"} found`,
        ...matches
          .slice(0, 8)
          .map(
            (entry) =>
              `${entry.id}  ${formatDisplayDate(entry.publishedAt)}  ${entry.authorLabel}  ${entry.folderPath} :: ${entry.title}`,
          ),
      ]);
      return;
    }

    if (command === "open") {
      const result = resolveOpenTarget(entries, argument);

      if ("error" in result) {
        appendOutput([result.error]);
        return;
      }

      if (!result.entry.sourceUrl) {
        appendOutput([`no source URL available for "${result.entry.title}"`]);
        return;
      }

      window.open(result.entry.sourceUrl, "_blank", "noopener,noreferrer");
      startTransition(() => setSelectedSlug(result.entry.slug));
      appendOutput([`opening ${result.entry.title}`]);
      return;
    }

    appendOutput([`unknown command: ${command}`, "type `help` for commands"]);
  }

  return (
    <section className="space-y-4">
      <div className="rounded-[2rem] border border-dashed border-white/15 bg-white/[0.045] p-6 shell-glow backdrop-blur-xl sm:p-8">
        <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-white/38">knowledge vault</p>
            <h1 className="mt-4 max-w-4xl text-3xl font-semibold leading-tight sm:text-4xl">
              Quiet source material, indexed like a terminal and browsed like a commit log.
            </h1>
            <p className="mt-4 max-w-3xl text-sm leading-7 text-white/58 sm:text-[15px]">
              Use the terminal to inspect the vault structure, open the original source material, and scan the log below
              when you want a fast editorial pass across the full archive.
            </p>
          </div>

          <div className="flex items-center gap-3 text-sm text-white/54">
            <span>{entries.length} indexed files</span>
            <span className="h-4 w-px bg-white/12" />
            <span>terminal + git log</span>
          </div>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1.4fr)_340px]">
        <section
          className="min-w-0 rounded-[2rem] border border-dashed border-white/15 bg-white/[0.045] shell-glow backdrop-blur-xl"
          onClick={() => terminalInputRef.current?.focus()}
        >
          <div className="relative flex items-center rounded-t-[2rem] border-b border-dashed border-white/12 px-4 py-3 text-xs text-white/42 sm:px-5">
            <div className="flex items-center gap-2">
              <span className="h-3 w-3 rounded-full bg-[#ff5f57]" />
              <span className="h-3 w-3 rounded-full bg-[#febc2e]" />
              <span className="h-3 w-3 rounded-full bg-[#28c840]" />
            </div>
            <div className="pointer-events-none absolute inset-x-0 flex items-center justify-center">
              <div className="flex items-center gap-2 uppercase tracking-[0.28em] text-white/45">
                <Command className="h-3.5 w-3.5" />
                <span>ochoa@vault</span>
              </div>
            </div>
          </div>

          <div className="px-4 py-4 sm:px-5">
            <div
              className="h-[420px] overflow-x-hidden overflow-y-auto rounded-[12px] border border-white/12 bg-[#0d0d0d] px-4 py-4 sm:px-5"
              ref={terminalViewportRef}
            >
              <div className="space-y-3 text-sm leading-7 text-[#33ff33]">
                {terminalLines.map((line) =>
                  line.kind === "command" ? (
                    <div className="flex gap-3 break-words" key={line.id}>
                      <span className="shrink-0 text-terminal">{line.prompt}</span>
                      <span>{line.displayText}</span>
                    </div>
                  ) : (
                    <p
                      className={`whitespace-pre-wrap break-words ${
                        line.id.startsWith("boot-") ? "text-[#33ff33]/86" : "text-[#33ff33]/72"
                      }`}
                      key={line.id}
                    >
                      {line.displayText}
                      {line.isTyping ? <span className="ml-0.5 inline-block h-5 w-2 animate-pulse bg-[#33ff33] align-middle" /> : null}
                    </p>
                  ),
                )}
              </div>
            </div>

            <form className="mt-4" onSubmit={handleCommandSubmit}>
              <label className="flex items-center gap-3 rounded-[12px] border border-white/12 bg-[#0d0d0d] px-4 py-3 text-sm text-[#33ff33]">
                <span className="shrink-0 text-terminal">{PROMPT}</span>
                <input
                  autoCapitalize="none"
                  autoCorrect="off"
                  className="min-w-0 flex-1 bg-transparent text-[#33ff33] outline-none placeholder:text-[#33ff33]/35"
                  onChange={(event) => setTerminalInput(event.target.value)}
                  placeholder="help"
                  ref={terminalInputRef}
                  spellCheck={false}
                  value={terminalInput}
                />
                <span aria-hidden className="h-5 w-2 animate-pulse bg-[#33ff33]" />
              </label>
            </form>
          </div>
        </section>

        <aside className="min-w-0 rounded-[2rem] border border-dashed border-white/15 bg-white/[0.045] p-5 shell-glow backdrop-blur-xl">
          <p className="text-[11px] uppercase tracking-[0.35em] text-white/38">selected source</p>

          {selectedEntry ? (
            <>
              <div className="mt-4 rounded-[1.45rem] border border-dashed border-white/12 bg-black/30 p-4">
                <p className="text-[11px] uppercase tracking-[0.3em] text-white/34">{selectedEntry.folderPath}</p>
                <h2 className="mt-3 text-lg font-semibold leading-7 text-white">{selectedEntry.title}</h2>
                <p className="mt-3 text-sm leading-7 text-white/58">{selectedEntry.authorLabel}</p>
                <p className="text-sm text-white/42">{formatDisplayDate(selectedEntry.publishedAt)}</p>
              </div>

              <div className="mt-4 space-y-3 rounded-[1.45rem] border border-dashed border-white/12 bg-white/[0.035] p-4 text-sm text-white/56">
                <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between sm:gap-3">
                  <span>hash</span>
                  <span className="break-all text-white/82 sm:text-right">{selectedEntry.id}</span>
                </div>
                <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between sm:gap-3">
                  <span>topic</span>
                  <span className="break-words text-white/82 sm:text-right">{selectedEntry.topic}</span>
                </div>
                <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between sm:gap-3">
                  <span>file</span>
                  <span className="break-all text-white/82 sm:text-right">{selectedEntry.fileName}.md</span>
                </div>
              </div>

              {selectedEntry.sourceUrl ? (
                <a
                  className="mt-4 inline-flex items-center gap-2 rounded-full border border-dashed border-white/16 bg-white/[0.04] px-4 py-2 text-sm text-white/82 transition hover:border-white/26 hover:bg-white/[0.08]"
                  href={selectedEntry.sourceUrl}
                  rel="noreferrer"
                  target="_blank"
                >
                  <span>open source</span>
                  <ArrowUpRight className="h-4 w-4" />
                </a>
              ) : (
                <p className="mt-4 text-sm text-white/40">No source URL available for this entry.</p>
              )}
            </>
          ) : (
            <p className="mt-4 text-sm text-white/48">No vault entries were loaded.</p>
          )}

          <div className="mt-5 rounded-[1.45rem] border border-dashed border-white/12 bg-white/[0.03] p-4 text-sm leading-7 text-white/54">
            Use `ls`, `find`, and `open` in the terminal. Clicking any log row below also updates this panel.
          </div>
        </aside>
      </div>

      <section className="rounded-[2rem] border border-dashed border-white/15 bg-white/[0.045] p-5 shell-glow backdrop-blur-xl sm:p-6">
        <div className="flex flex-col gap-4 border-b border-dashed border-white/12 pb-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <p className="text-[11px] uppercase tracking-[0.35em] text-white/38">&gt; vault log</p>
              <span className="rounded-full border border-dashed border-white/12 px-3 py-1 text-[11px] uppercase tracking-[0.24em] text-white/44">
                {entries.length} entries
              </span>
            </div>
            <p className="mt-2 text-sm leading-7 text-white/56">Filter by topic, title, or author. Open the source when a line is useful.</p>
          </div>

          <div className="flex flex-col gap-3 lg:min-w-[420px] lg:max-w-[420px]">
            <label className="flex items-center gap-3 rounded-[1.2rem] border border-dashed border-white/12 bg-black/30 px-4 py-3 text-sm text-white/58 backdrop-blur-xl">
              <Search className="h-4 w-4" />
              <input
                className="min-w-0 flex-1 bg-transparent text-white outline-none placeholder:text-white/24"
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search title or author"
                type="search"
                value={query}
              />
            </label>

            <div className="flex flex-wrap gap-2">
              {TOPIC_FILTERS.map((topic) => (
                <button
                  className={`rounded-full border border-dashed px-3 py-2 text-xs uppercase tracking-[0.24em] transition ${
                    activeTopic === topic
                      ? "border-white/24 bg-white/12 text-white"
                      : "border-white/10 bg-white/[0.03] text-white/48 hover:border-white/18 hover:text-white/80"
                  }`}
                  key={topic}
                  onClick={() => setActiveTopic(topic)}
                  type="button"
                >
                  {topic}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-5 space-y-3">
          <div className="max-h-[580px] space-y-3 overflow-y-auto pr-1">
            {filteredEntries.length ? (
              filteredEntries.map((entry) => (
                <article
                  className={`rounded-[1.45rem] border border-dashed px-4 py-4 transition ${
                    selectedEntry?.slug === entry.slug
                      ? "border-white/22 bg-white/[0.08]"
                      : "border-white/10 bg-black/25 hover:bg-white/[0.04]"
                  }`}
                  key={entry.slug}
                >
                  <button className="block w-full text-left" onClick={() => startTransition(() => setSelectedSlug(entry.slug))} type="button">
                    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-white/34">
                      <span className="font-medium uppercase tracking-[0.18em]">#{entry.id}</span>
                      <span>{formatDisplayDate(entry.publishedAt)}</span>
                      <span>{entry.authorLabel}</span>
                      <span className="truncate uppercase tracking-[0.18em]">{entry.folderPath}</span>
                    </div>
                    <p className="mt-3 text-[13px] leading-6 text-white/90">{entry.title}</p>
                  </button>
                  {entry.sourceUrl ? (
                    <a
                      className="mt-3 inline-flex items-center gap-2 text-[11px] text-white/42 transition hover:text-white"
                      href={entry.sourceUrl}
                      rel="noreferrer"
                      target="_blank"
                    >
                      <span>{`→ ${new URL(entry.sourceUrl).hostname.replace(/^www\./, "")}`}</span>
                    </a>
                  ) : (
                    <span className="mt-3 inline-flex text-[11px] text-white/24">→ no-source</span>
                  )}
                </article>
              ))
            ) : (
              <div className="rounded-[1.45rem] border border-dashed border-white/10 bg-black/25 px-4 py-8 text-sm text-white/44">
                No entries match the current filters.
              </div>
            )}
          </div>
        </div>

        <div className="mt-4 flex items-center justify-between gap-3 text-xs uppercase tracking-[0.22em] text-white/34">
          <span>{filteredEntries.length} visible entries</span>
          <Link className="text-white/52 transition hover:text-white/84" href="/">
            return home
          </Link>
        </div>
      </section>
    </section>
  );
}
