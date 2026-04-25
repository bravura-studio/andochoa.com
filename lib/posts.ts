import fs from "node:fs";
import path from "node:path";
import matter from "gray-matter";

export type PostStatus = "published" | "draft";

export type Post = {
  slug: string;
  title: string;
  date: string;
  status: PostStatus;
  type: string;
  description: string;
  excerpt: string;
  content: string;
  wordCount: number;
  readingTimeMinutes: number;
};

const CONTENT_ROOT = path.join(process.cwd(), "content");
const SOURCES: Array<{ dir: string; status: PostStatus }> = [
  { dir: path.join(CONTENT_ROOT, "published"), status: "published" },
  { dir: path.join(CONTENT_ROOT, "drafts"), status: "draft" },
];

function titleizeFilename(value: string) {
  return value
    .replace(/[-_]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function findMarkdownFiles(dir: string): string[] {
  if (!fs.existsSync(dir)) {
    return [];
  }

  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const fullPath = path.join(dir, entry.name);

    if (entry.isDirectory()) {
      return findMarkdownFiles(fullPath);
    }

    const extension = path.extname(entry.name).toLowerCase();

    if (
      !entry.isFile() ||
      (extension !== ".md" && extension !== ".mdx") ||
      entry.name.toLowerCase() === "readme.md" ||
      entry.name.toLowerCase() === "readme.mdx"
    ) {
      return [];
    }

    return [fullPath];
  });
}

function extractExcerpt(content: string) {
  const lines = content
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith("#") && !line.startsWith(">") && !line.startsWith("*"));

  return lines[0] ?? "Writing in progress.";
}

function countWords(content: string) {
  return content
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/`[^`]+`/g, " ")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .split(/\s+/)
    .map((token) => token.trim())
    .filter(Boolean).length;
}

function computeReadingTime(wordCount: number) {
  return Math.max(1, Math.ceil(wordCount / 200));
}

function readPost(filePath: string, sourceDir: string, fallbackStatus: PostStatus): Post {
  const file = fs.readFileSync(filePath, "utf8");
  const { data, content } = matter(file);
  const filename = path.basename(filePath, path.extname(filePath));
  const relativeSlug = path.relative(sourceDir, filePath).replace(/\\/g, "/").replace(/\.(md|mdx)$/, "");
  const heading = content
    .split("\n")
    .find((line) => line.trim().startsWith("# "))
    ?.replace(/^#\s+/, "")
    .trim();
  const title = typeof data.title === "string" ? data.title : heading ?? titleizeFilename(filename);
  const rawDate = data.date ?? data.revised ?? fs.statSync(filePath).mtime.toISOString();
  const date = new Date(rawDate).toISOString();
  const status = data.status === "published" ? "published" : fallbackStatus;
  const excerpt = extractExcerpt(content);
  const wordCount =
    typeof data.word_count === "number" && Number.isFinite(data.word_count) ? data.word_count : countWords(content);

  return {
    slug: relativeSlug,
    title,
    date,
    status,
    type: typeof data.type === "string" ? data.type : "reflection",
    description: typeof data.description === "string" ? data.description : excerpt,
    excerpt,
    content,
    wordCount,
    readingTimeMinutes: computeReadingTime(wordCount),
  };
}

export function getAllPosts() {
  return SOURCES.flatMap(({ dir, status }) => findMarkdownFiles(dir).map((filePath) => readPost(filePath, dir, status)))
    .sort((left, right) => new Date(right.date).getTime() - new Date(left.date).getTime());
}

export function getRecentPublishedPosts(limit = 3) {
  return getAllPosts()
    .filter((post) => post.status === "published")
    .slice(0, limit);
}

export function getPostBySlug(slug: string) {
  return getAllPosts().find((post) => post.slug === slug) ?? null;
}
