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
    <aside className="overflow-hidden rounded-2xl border border-dashed border-white/10 bg-white/[0.03] shadow-terminal backdrop-blur-xl lg:h-full">
      <div className="border-b border-dashed border-white/10 px-4 py-4">
        <p className="text-[10px] uppercase tracking-[0.32em] text-white/38">post navigator</p>
        <label className="mt-4 block">
          <span className="sr-only">Search posts</span>
          <input
            className="w-full rounded-lg border border-dashed border-white/12 bg-white/[0.04] px-3 py-2.5 text-[12px] text-white outline-none transition placeholder:text-white/28 focus:border-white/24"
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
                  "rounded-full border border-dashed px-2.5 py-1 text-[10px] uppercase tracking-[0.2em] transition",
                  isActive
                    ? "border-white/18 bg-white/[0.08] text-white"
                    : "border-white/10 bg-transparent text-white/46 hover:border-white/16 hover:bg-white/[0.05] hover:text-white/72",
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

      <div className="space-y-1 px-2 py-2">
        {filteredPosts.length > 0 ? (
          filteredPosts.map((post) => {
            const isSelected = post.slug === selectedSlug;

            return (
              <Link
                className={cn(
                  "block rounded-xl border border-transparent px-3 py-3 transition",
                  isSelected
                    ? "border-l-2 border-l-white bg-white/[0.06] text-white"
                    : "text-white/72 hover:bg-white/[0.035] hover:text-white",
                )}
                href={`/posts/${post.slug}`}
                key={post.slug}
              >
                <p className="text-[10px] uppercase tracking-[0.18em] text-white/34">{formatDate(post.date)}</p>
                <h2 className="mt-2 text-[13px] font-medium text-white">{post.title}</h2>
                <p className="mt-2 text-[11px] leading-5 text-white/48">{post.description}</p>
              </Link>
            );
          })
        ) : (
          <div className="rounded-xl border border-dashed border-white/10 bg-black/25 px-4 py-5 text-sm leading-7 text-white/52">
            No posts match the current search and tag filter.
          </div>
        )}
      </div>
    </aside>
  );
}
