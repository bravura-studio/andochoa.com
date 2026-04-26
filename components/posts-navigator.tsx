"use client";

import Link from "next/link";
import { useState } from "react";
import type { Post } from "@/lib/posts";
import { cn } from "@/lib/utils";

function formatDate(date: string) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
  }).format(new Date(date));
}

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

      <div className="space-y-1 px-1 py-3">
        {filteredPosts.length > 0 ? (
          filteredPosts.map((post) => {
            const isSelected = post.slug === selectedSlug;

            return (
              <Link
                className={cn(
                  "block rounded-md border border-transparent px-3 py-3 transition",
                  isSelected
                    ? "border-white/10 bg-white/[0.06] text-white"
                    : "text-white/62 hover:border-white/8 hover:bg-white/[0.04] hover:text-white",
                )}
                href={`/posts/${post.slug}`}
                key={post.slug}
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="text-[10px] uppercase tracking-[0.18em] text-white/28">{formatDate(post.date)}</p>
                  <span className="rounded-md border border-white/8 px-2 py-0.5 text-[9px] uppercase tracking-[0.18em] text-white/30">
                    {post.type}
                  </span>
                </div>
                <h2 className="mt-2 text-[13px] text-white">{post.title}</h2>
                <p className="mt-1 text-[11px] leading-5 text-white/42">{post.description}</p>
              </Link>
            );
          })
        ) : (
          <div className="rounded-md border border-dashed border-white/10 bg-white/[0.03] px-4 py-5 text-[11px] leading-6 text-white/42">
            No posts match the current search and tag filter.
          </div>
        )}
      </div>
    </aside>
  );
}
