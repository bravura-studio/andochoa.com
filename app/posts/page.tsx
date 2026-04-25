import { PostsWorkspace } from "@/components/posts-workspace";
import { getAllPosts } from "@/lib/posts";

export default function PostsPage() {
  const posts = getAllPosts();

  return <PostsWorkspace posts={posts} selectedSlug={posts[0]?.slug ?? null} />;
}
