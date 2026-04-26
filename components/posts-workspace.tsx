import Link from "next/link";
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
  const fallbackPost = posts[0] ?? null;
  const selectedPost = posts.find((post) => post.slug === selectedSlug) ?? fallbackPost;
  const fileLabel = selectedPost ? `${selectedPost.slug.split("/").at(-1)}.md` : "posts";
  const statusMeta = selectedPost
    ? `${selectedPost.wordCount} words · ${selectedPost.readingTimeMinutes} min`
    : `${posts.length} posts`;

  return (
    <SiteShell
      activityKey="posts"
      breadcrumbs={[
        { label: "andochoa.com", href: "/" },
        { label: "posts", href: "/posts" },
        { label: fileLabel },
      ]}
      sidebar={<PostsNavigator posts={posts} selectedSlug={selectedPost?.slug ?? null} />}
      sidebarTitle="posts"
      statusMeta={statusMeta}
      tabs={[
        { href: "/posts", label: "posts/" },
        { active: true, label: fileLabel },
      ]}
    >
      <div className="hidden lg:block">{selectedPost ? <PostReader post={selectedPost} /> : null}</div>

      <div className="lg:hidden">
        {showMobileReader && selectedPost ? (
          <div>
            <Link className="mb-4 inline-flex text-[11px] uppercase tracking-[0.2em] text-white/36" href="/posts">
              ← back to posts
            </Link>
            <PostReader post={selectedPost} />
          </div>
        ) : (
          <PostsNavigator posts={posts} selectedSlug={selectedPost?.slug ?? null} />
        )}
      </div>
    </SiteShell>
  );
}
