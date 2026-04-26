import { PostsWorkspace } from "@/components/posts-workspace";
import { getPublishedPosts } from "@/lib/posts";
import { buildPageMetadata } from "@/lib/site";

export const metadata = buildPageMetadata({
  title: "Posts",
  description: "Published essays from Andre Ochoa's founder writing workspace.",
  path: "/posts",
});

export default function PostsPage() {
  const posts = getPublishedPosts();

  return <PostsWorkspace posts={posts} selectedSlug={posts[0]?.slug ?? null} />;
}
