"use client";

import Link from "next/link";
import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { formatIsoDate } from "@/lib/date";
import type { Post } from "@/lib/posts";
import { cn } from "@/lib/utils";

type PostsNavigatorProps = {
  posts: Post[];
  selectedSlug: string | null;
  onPostClick?: () => void;
};

export function PostsNavigator({ posts, selectedSlug, onPostClick }: PostsNavigatorProps) {
  const [query, setQuery] = useState("");
  const tagOptions = ["all", ...new Set(posts.flatMap((post) => post.tags))];
  const [activeFilter, setActiveFilter] = useState("all");
  const [folderOpen, setFolderOpen] = useState(true);
  const [focusedIndex, setFocusedIndex] = useState<number | null>(null);
  const router = useRouter();
  const selectedRef = useRef<HTMLAnchorElement | null>(null);
  const focusedItemRef = useRef<HTMLAnchorElement | null>(null);

  const filteredPosts = posts.filter((post) => {
    const normalizedQuery = query.trim().toLowerCase();
    const matchesQuery =
      !normalizedQuery ||
      post.title.toLowerCase().includes(normalizedQuery) ||
      post.description.toLowerCase().includes(normalizedQuery) ||
      post.content.toLowerCase().includes(normalizedQuery);
    const matchesFilter = activeFilter === "all" || post.tags.includes(activeFilter);

    return matchesQuery && matchesFilter;
  });

  // Fix 2: Scroll sync — scroll selected post into view when selectedSlug changes
  useEffect(() => {
    selectedRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [selectedSlug]);

  // Fix 4: Keyboard nav — scroll focused item into view when focusedIndex changes
  useEffect(() => {
    focusedItemRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [focusedIndex]);

  // Fix 4: Keyboard navigation — ↑/↓ cycle posts, Enter opens focused post
  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent) => {
      if (!folderOpen) return;

      if (event.key === "ArrowDown") {
        event.preventDefault();
        setFocusedIndex((prev) => (prev === null ? 0 : Math.min(prev + 1, filteredPosts.length - 1)));
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        setFocusedIndex((prev) => (prev === null ? filteredPosts.length - 1 : Math.max(prev - 1, 0)));
      } else if (event.key === "Enter" && focusedIndex !== null) {
        event.preventDefault();
        const post = filteredPosts[focusedIndex];

        if (post) {
          router.push(`/posts/${post.slug}`);
          onPostClick?.();
        }
      }
    },
    [filteredPosts, focusedIndex, folderOpen, router, onPostClick],
  );

  return (
    <aside className="outline-none" onKeyDown={handleKeyDown} tabIndex={0}>
      {/* Fix 7: search + filters above the file tree */}
      <div className="border-b border-white/7 px-2 pb-3">
        <label className="block">
          <span className="sr-only">Search posts</span>
          <input
            className="w-full rounded-md border border-white/8 bg-white/[0.03] px-3 py-2 text-[11px] text-white outline-none transition placeholder:text-white/22 focus:border-white/14"
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search posts"
            type="search"
            value={query}
          />
        </label>

        <div className="mt-2 flex flex-wrap gap-1.5">
          {tagOptions.map((filter) => {
            const isActive = filter === activeFilter;

            return (
              <button
                className={cn(
                  "rounded px-2 py-0.5 text-[10px] uppercase tracking-[0.2em] transition",
                  isActive
                    ? "bg-white/[0.08] text-white"
                    : "text-white/34 hover:bg-white/[0.04] hover:text-white/68",
                )}
                key={filter}
                onClick={() => setActiveFilter(filter)}
                type="button"
              >
                {filter}
              </button>
            );
          })}
        </div>
      </div>

      {/* Fix 5 + 6: collapsible folder header with post count */}
      <div className="px-1 py-2">
        <button
          className="flex w-full items-center rounded px-3 py-1.5 text-left text-[12px] text-white/40 transition hover:text-white/60"
          onClick={() => setFolderOpen((prev) => !prev)}
          type="button"
        >
          {folderOpen ? "▾" : "▸"} posts/ ({filteredPosts.length})
        </button>

        {folderOpen && filteredPosts.length > 0 ? (
          <div className="ml-3 mt-0.5">
            {filteredPosts.map((post, index) => {
              const isSelected = post.slug === selectedSlug;
              const isFocused = index === focusedIndex;

              return (
                <Link
                  className={cn(
                    "block border-l-2 py-2 pl-3 pr-2 transition",
                    isSelected
                      ? "border-l-white bg-white/[0.06] text-white"
                      : cn(
                          isFocused
                            ? "border-l-white/30 bg-white/[0.04] text-white"
                            : "border-l-transparent text-white/62 hover:border-l-white/20 hover:bg-white/[0.04] hover:text-white",
                        ),
                  )}
                  href={`/posts/${post.slug}`}
                  key={post.slug}
                  onClick={onPostClick}
                  ref={(el) => {
                    if (isSelected) selectedRef.current = el;
                    if (isFocused) focusedItemRef.current = el;
                  }}
                  title={post.description}
                >
                  <p className={cn("truncate text-[12px] leading-tight", isSelected ? "font-bold text-white" : "text-white")}>
                    {post.title}
                  </p>
                  <p className="mt-0.5 text-[10px] text-white/34">
                    {formatIsoDate(post.date)} · {post.type}
                  </p>
                </Link>
              );
            })}
          </div>
        ) : null}

        {folderOpen && filteredPosts.length === 0 ? (
          <div className="mt-1 rounded border border-dashed border-white/10 bg-white/[0.03] px-4 py-4 text-[11px] leading-6 text-white/42">
            no posts found
          </div>
        ) : null}
      </div>
    </aside>
  );
}
