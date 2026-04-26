"use client";

import { useState } from "react";
import type { Post } from "@/lib/posts";
import { PostReader } from "@/components/post-reader";
import { PostsNavigator } from "@/components/posts-navigator";
import { SiteShell } from "@/components/site-shell";

type PostsWorkspaceProps = {
  posts: Post[];
  selectedSlug?: string | null;
  showMobileReader?: boolean;
};

export function PostsWorkspace({
  posts,
  selectedSlug = null,
  showMobileReader = false,
}: PostsWorkspaceProps) {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  const fallbackPost = posts[0] ?? null;
  const selectedPost = posts.find((post) => post.slug === selectedSlug) ?? fallbackPost;
  const selectedIndex = selectedPost ? posts.findIndex((post) => post.slug === selectedPost.slug) : -1;
  const previousPost = selectedIndex >= 0 ? (posts[selectedIndex + 1] ?? null) : null;
  const nextPost = selectedIndex > 0 ? (posts[selectedIndex - 1] ?? null) : null;
  const fileLabel = selectedPost?.filename ?? "posts";
  const statusMeta = selectedPost
    ? `${selectedPost.wordCount} words · ${selectedPost.readingTimeMinutes} min · ${selectedPost.type}`
    : `${posts.length} posts`;

  const navigator = (
    <PostsNavigator
      onPostClick={() => setMobileSidebarOpen(false)}
      posts={posts}
      selectedSlug={selectedPost?.slug ?? null}
    />
  );

  return (
    <SiteShell
      activityKey="posts"
      breadcrumbs={[
        { label: "andochoa.com", href: "/" },
        { label: "posts", href: "/posts" },
        { label: fileLabel },
      ]}
      mobileSidebarOpen={mobileSidebarOpen}
      onMobileSidebarOpenChange={setMobileSidebarOpen}
      sidebar={navigator}
      sidebarTitle="posts"
      statusMeta={statusMeta}
      tabs={[{ active: true, href: selectedPost ? `/posts/${selectedPost.slug}` : "/posts", label: fileLabel }]}
    >
      {showMobileReader && selectedPost ? (
        <div>
          <button
            className="mb-4 inline-flex text-[11px] uppercase tracking-[0.2em] text-white/36 transition hover:text-white/68 lg:hidden"
            onClick={() => setMobileSidebarOpen(true)}
            type="button"
          >
            ← posts
          </button>
          <PostReader nextPost={nextPost} post={selectedPost} previousPost={previousPost} />
        </div>
      ) : null}

      {!showMobileReader && selectedPost ? (
        <div className="hidden lg:block">
          <PostReader nextPost={nextPost} post={selectedPost} previousPost={previousPost} />
        </div>
      ) : null}

      {!showMobileReader ? (
        <div className="lg:hidden">
          {navigator}
        </div>
      ) : null}
    </SiteShell>
  );
}
