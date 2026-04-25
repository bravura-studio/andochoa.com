import fs from "node:fs";
import path from "node:path";
import matter from "gray-matter";

export type PostStatus = "published" | "draft";

export type Post = {
  slug: string;
  title: string;
  date: string;
  status: PostStatus;
  excerpt: string;
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

    if (!entry.isFile() || path.extname(entry.name) !== ".md" || entry.name.toLowerCase() === "readme.md") {
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

function readPost(filePath: string, fallbackStatus: PostStatus): Post {
  const file = fs.readFileSync(filePath, "utf8");
  const { data, content } = matter(file);
  const filename = path.basename(filePath, ".md");
  const relativeSlug = path.relative(CONTENT_ROOT, filePath).replace(/\\/g, "/").replace(/\.md$/, "");
  const heading = content
    .split("\n")
    .find((line) => line.trim().startsWith("# "))
    ?.replace(/^#\s+/, "")
    .trim();
  const title = typeof data.title === "string" ? data.title : heading ?? titleizeFilename(filename);
  const rawDate = data.date ?? data.revised ?? fs.statSync(filePath).mtime.toISOString();
  const date = new Date(rawDate).toISOString();
  const status = data.status === "published" ? "published" : fallbackStatus;

  return {
    slug: relativeSlug,
    title,
    date,
    status,
    excerpt: extractExcerpt(content),
  };
}

export function getAllPosts() {
  return SOURCES.flatMap(({ dir, status }) => findMarkdownFiles(dir).map((filePath) => readPost(filePath, status))).sort(
    (left, right) => new Date(right.date).getTime() - new Date(left.date).getTime(),
  );
}

export function getRecentPublishedPosts(limit = 3) {
  return getAllPosts()
    .filter((post) => post.status === "published")
    .slice(0, limit);
}
