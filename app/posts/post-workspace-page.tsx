import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { PostsWorkspace } from "@/components/posts-workspace";
import { getPostBySlug, getPublishedPosts } from "@/lib/posts";
import { siteConfig } from "@/lib/site";

export function buildPostWorkspaceMetadata(resolvedSlug: string): Metadata {
  const post = getPostBySlug(resolvedSlug);

  if (!post) {
    return {
      title: "Post not found",
      description: siteConfig.description,
    };
  }

  const path = `/posts/${resolvedSlug}`;

  return {
    title: post.title,
    description: post.description,
    alternates: {
      canonical: path,
    },
    openGraph: {
      title: `${post.title} | ${siteConfig.name}`,
      description: post.description,
      url: path,
      siteName: siteConfig.name,
      images: [siteConfig.ogImagePath],
      type: "article",
      publishedTime: post.date,
    },
    twitter: {
      card: "summary_large_image",
      title: `${post.title} | ${siteConfig.name}`,
      description: post.description,
      images: [siteConfig.ogImagePath],
    },
  };
}

export function renderPostWorkspacePage(resolvedSlug: string) {
  const post = getPostBySlug(resolvedSlug);

  if (!post) {
    notFound();
  }

  return <PostsWorkspace posts={getPublishedPosts()} selectedSlug={resolvedSlug} showMobileReader />;
}
