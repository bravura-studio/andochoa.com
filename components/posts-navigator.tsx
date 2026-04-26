"use client";

import Link from "next/link";
import { useState } from "react";
import { formatIsoDate } from "@/lib/date";
import type { Post } from "@/lib/posts";
import { cn } from "@/lib/utils";

type PostsNavigatorProps = {
  posts: Post[];
  selectedSlug: string | null;
};

export function PostsNavigator({ posts, selectedSlug }: PostsNavigatorProps) {
  const [query, setQuery] = useState("");
  const tagOptions = ["all", ...new Set(posts.flatMap((post) => post.tags))];
  const [activeFilter, setActiveFilter] = useState("all");

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

  return (
    <aside>
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

      {/* Fix 3/6: file-explorer tree aesthetic */}
      <div className="px-1 py-2">
        {/* ▾ expanded folder header */}
        <div className="px-3 py-1.5 text-[12px] text-white/40">▾ posts/</div>

        {filteredPosts.length > 0 ? (
          <div className="ml-3 mt-0.5">
            {filteredPosts.map((post) => {
              const isSelected = post.slug === selectedSlug;

              return (
                <Link
                  className={cn(
                    "block border-l-2 py-2 pl-3 pr-2 transition",
                    // Fix 8: 2px left border accent on active
                    isSelected
                      ? "border-l-white bg-white/[0.04] text-white"
                      : "border-l-transparent text-white/62 hover:border-l-white/20 hover:bg-white/[0.04] hover:text-white",
                  )}
                  href={`/posts/${post.slug}`}
                  key={post.slug}
                >
                  {/* Fix 1: title not filename; Fix 2: compact two-line layout */}
                  <p className="truncate text-[12px] leading-tight text-white">{post.title}</p>
                  <p className="mt-0.5 text-[10px] text-white/34">
                    {formatIsoDate(post.date)} · {post.type}
                  </p>
                </Link>
              );
            })}
          </div>
        ) : (
          <div className="mt-1 rounded-md border border-dashed border-white/10 bg-white/[0.03] px-4 py-5 text-[11px] leading-6 text-white/42">
            no posts found
          </div>
        )}
      </div>
    </aside>
  );
}
