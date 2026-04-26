"use client";

import Link from "next/link";
import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { formatIsoDate } from "@/lib/date";
import { getPostTypeBadgeClassName } from "@/lib/post-type-styles";
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
      <div className="border-b border-white/7 px-2 pb-3">
        <p className="text-[10px] uppercase tracking-[0.28em] text-white/28">post navigator</p>
        <label className="mt-4 block">
          <span className="sr-only">Search posts</span>
          <input
            className="w-full rounded-md border border-white/8 bg-white/[0.03] px-3 py-2 text-[11px] text-white outline-none transition placeholder:text-white/22 focus:border-white/14"
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search posts"
            type="search"
            value={query}
          />
        </label>

        <div className="mt-4 flex flex-wrap gap-2">
          {tagOptions.map((filter) => {
            const isActive = filter === activeFilter;

            return (
              <button
                className={cn(
                  "rounded-md border px-2.5 py-1 text-[10px] uppercase tracking-[0.2em] transition",
                  isActive
                    ? "border-white/14 bg-white/[0.06] text-white"
                    : "border-white/8 bg-transparent text-white/34 hover:border-white/14 hover:bg-white/[0.04] hover:text-white/68",
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

      <div className="px-1 py-3">
        {/* Fix 5 + 6: collapsible folder header with post count */}
        <button
          className="flex w-full items-center rounded-md px-3 py-2 text-left text-[12px] text-white/40 transition hover:text-white/60"
          onClick={() => setFolderOpen((prev) => !prev)}
          type="button"
        >
          {folderOpen ? "▾" : "▸"} posts/ ({filteredPosts.length})
        </button>

        {folderOpen && filteredPosts.length > 0 ? (
          <div className="mt-1 space-y-1">
            {filteredPosts.map((post, index) => {
              const isSelected = post.slug === selectedSlug;
              const isFocused = index === focusedIndex;

              return (
                <Link
                  className={cn(
                    "block rounded-md px-3 py-3 transition",
                    isSelected
                      ? "border-l-2 border-l-white bg-white/[0.06]"
                      : cn(
                          "border border-transparent",
                          isFocused
                            ? "border-white/14 bg-white/[0.04] text-white"
                            : "text-white/62 hover:border-white/8 hover:bg-white/[0.04] hover:text-white",
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
                  <div className="flex items-start gap-2">
                    <span className={cn("pt-0.5 text-[12px]", isSelected ? "text-white/50" : "text-white/28")}>▸</span>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-start justify-between gap-3">
                        <p className={cn("truncate text-[12px]", isSelected ? "font-bold text-white" : "text-white")}>
                          {post.filename}
                        </p>
                        <span className={getPostTypeBadgeClassName(post.type)}>{post.type}</span>
                      </div>
                      <p className="mt-2 text-[10px] uppercase tracking-[0.18em] text-white/28">{formatIsoDate(post.date)}</p>
                      <p
                        className="mt-2 overflow-hidden text-[11px] leading-5 text-white/42"
                        style={{
                          WebkitBoxOrient: "vertical",
                          WebkitLineClamp: 2,
                          display: "-webkit-box",
                        }}
                      >
                        {post.description}
                      </p>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        ) : null}

        {folderOpen && filteredPosts.length === 0 ? (
          <div className="mt-1 rounded-md border border-dashed border-white/10 bg-white/[0.03] px-4 py-5 text-[11px] leading-6 text-white/42">
            no posts found
          </div>
        ) : null}
      </div>
    </aside>
  );
}
