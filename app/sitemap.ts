import type { MetadataRoute } from "next";
import { getPublishedPosts } from "@/lib/posts";

const BASE_URL = "https://andochoa.com";

export default function sitemap(): MetadataRoute.Sitemap {
  const posts = getPublishedPosts();

  const postEntries: MetadataRoute.Sitemap = posts.map((post) => ({
    url: `${BASE_URL}/posts/${post.slug}`,
    lastModified: new Date(post.date),
    changeFrequency: "monthly",
    priority: 0.7,
  }));

  return [
    {
      url: BASE_URL,
      lastModified: new Date(),
      changeFrequency: "weekly",
      priority: 1,
    },
    {
      url: `${BASE_URL}/posts`,
      lastModified: new Date(),
      changeFrequency: "weekly",
      priority: 0.8,
    },
    {
      url: `${BASE_URL}/about`,
      changeFrequency: "monthly",
      priority: 0.5,
    },
    {
      url: `${BASE_URL}/vault`,
      changeFrequency: "weekly",
      priority: 0.6,
    },
    ...postEntries,
  ];
}
