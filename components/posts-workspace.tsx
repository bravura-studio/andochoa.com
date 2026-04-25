import type { Post } from "@/lib/posts";
import { PostReader } from "@/components/post-reader";
import { PostsNavigator } from "@/components/posts-navigator";

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

  return (
    <section className="min-h-[calc(100vh-8rem)]">
      <div className="grid gap-4 lg:min-h-[calc(100vh-9.5rem)] lg:grid-cols-[300px_minmax(0,1fr)]">
        <div className={showMobileReader ? "hidden lg:block" : undefined}>
          <PostsNavigator posts={posts} selectedSlug={selectedPost?.slug ?? null} />
        </div>

        <div className={showMobileReader ? undefined : "hidden lg:block"}>
          {selectedPost ? (
            <PostReader post={selectedPost} />
          ) : (
            <section className="rounded-[2rem] border border-dashed border-white/15 bg-white/[0.045] p-8 shadow-terminal backdrop-blur-xl">
              <p className="text-sm text-white/56">No post selected yet.</p>
            </section>
          )}
        </div>

        {showMobileReader && selectedPost ? (
          <div className="lg:hidden">
            <PostReader post={selectedPost} showMobileBackLink />
          </div>
        ) : null}
      </div>
    </section>
  );
}
