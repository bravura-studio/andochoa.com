"use client";

import Link from "next/link";
import { useState } from "react";
import type { Post } from "@/lib/posts";

const FILTERS = ["all", "reflection", "struggle", "win", "observation", "brainstorm"] as const;

function formatDate(date: string) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
  }).format(new Date(date));
}

function normalizeType(type: string) {
  return type.toLowerCase();
}

type PostsNavigatorProps = {
  posts: Post[];
  selectedSlug: string | null;
};

export function PostsNavigator({ posts, selectedSlug }: PostsNavigatorProps) {
  const [query, setQuery] = useState("");
  const [activeFilter, setActiveFilter] = useState<(typeof FILTERS)[number]>("all");

  const filteredPosts = posts.filter((post) => {
    const normalizedQuery = query.trim().toLowerCase();
    const matchesQuery =
      !normalizedQuery ||
      post.title.toLowerCase().includes(normalizedQuery) ||
      post.description.toLowerCase().includes(normalizedQuery);
    const matchesFilter = activeFilter === "all" || normalizeType(post.type) === activeFilter;

    return matchesQuery && matchesFilter;
  });

  return (
    <aside className="rounded-[2rem] border border-dashed border-white/15 bg-white/[0.045] p-4 shadow-terminal backdrop-blur-xl">
      <div className="border-b border-dashed border-white/10 pb-4">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-[11px] uppercase tracking-[0.35em] text-white/40">post navigator</p>
            <p className="mt-2 text-sm text-white/72">Search the archive and jump into a single post.</p>
          </div>
          <span className="rounded-full border border-dashed border-white/12 px-3 py-1 text-[11px] uppercase tracking-[0.24em] text-white/48">
            {filteredPosts.length} visible
          </span>
        </div>

        <label className="mt-4 block">
          <span className="sr-only">Search posts</span>
          <input
            className="w-full rounded-[1.2rem] border border-dashed border-white/14 bg-black/35 px-4 py-3 text-sm text-white outline-none transition placeholder:text-white/28 focus:border-white/24"
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search title or description"
            type="search"
            value={query}
          />
        </label>

        <div className="mt-4 flex flex-wrap gap-2">
          {FILTERS.map((filter) => {
            const isActive = filter === activeFilter;

            return (
              <button
                className={`rounded-full border border-dashed px-3 py-2 text-[11px] uppercase tracking-[0.24em] transition ${
                  isActive
                    ? "border-white/22 bg-white/10 text-white"
                    : "border-white/10 bg-white/[0.03] text-white/50 hover:border-white/18 hover:text-white/78"
                }`}
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

      <div className="mt-4 space-y-3">
        {filteredPosts.length > 0 ? (
          filteredPosts.map((post) => {
            const isSelected = post.slug === selectedSlug;

            return (
              <Link
                className={`block rounded-[1.45rem] border border-dashed px-4 py-4 transition ${
                  isSelected
                    ? "border-white/24 bg-white/[0.08] text-white shadow-terminal"
                    : "border-white/10 bg-black/25 text-white/72 hover:border-white/18 hover:bg-white/[0.05] hover:text-white"
                }`}
                href={`/posts/${post.slug}`}
                key={post.slug}
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="text-[11px] uppercase tracking-[0.24em] text-white/38">{formatDate(post.date)}</p>
                  <span className="rounded-full border border-dashed border-white/12 px-2.5 py-1 text-[10px] uppercase tracking-[0.24em] text-white/44">
                    {normalizeType(post.type)}
                  </span>
                </div>
                <h2 className="mt-3 text-base font-medium text-white">{post.title}</h2>
                <p className="mt-2 text-sm leading-6 text-white/54">{post.description}</p>
              </Link>
            );
          })
        ) : (
          <div className="rounded-[1.45rem] border border-dashed border-white/10 bg-black/25 px-4 py-5 text-sm leading-7 text-white/52">
            No posts match the current search and tag filter.
          </div>
        )}
      </div>
    </aside>
  );
}
