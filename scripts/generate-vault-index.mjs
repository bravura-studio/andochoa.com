import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import matter from "gray-matter";

const VAULT_ROOT = "/knowledge/vault-scripta";
const INCLUDED_TOPICS = ["great-writing", "world-view"];
const OUTPUT_PATH = path.join(process.cwd(), "content", "vault-index.json");

function findMarkdownFiles(dir) {
  if (!fs.existsSync(dir)) {
    return [];
  }

  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const fullPath = path.join(dir, entry.name);

    if (entry.isDirectory()) {
      return findMarkdownFiles(fullPath);
    }

    if (!entry.isFile() || path.extname(entry.name).toLowerCase() !== ".md") {
      return [];
    }

    return [fullPath];
  });
}

function titleizeFilename(value) {
  return value
    .replace(/[-_]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function normalizeAuthor(value) {
  if (Array.isArray(value)) {
    return value
      .flatMap((item) => normalizeAuthor(item))
      .filter(Boolean);
  }

  if (typeof value !== "string") {
    return [];
  }

  const cleaned = value.replace(/\[\[|\]\]/g, "").trim();

  return cleaned ? [cleaned] : [];
}

function normalizeDate(value, filePath) {
  const fallback = fs.statSync(filePath).mtime.toISOString();

  if (!value) {
    return fallback;
  }

  const parsed = new Date(value);

  return Number.isNaN(parsed.getTime()) ? fallback : parsed.toISOString();
}

function createHash(relativePath) {
  return crypto.createHash("sha1").update(relativePath).digest("hex").slice(0, 7);
}

function readEntry(filePath) {
  const source = fs.readFileSync(filePath, "utf8");
  const { data } = matter(source);
  const relativePath = path.relative(VAULT_ROOT, filePath).replace(/\\/g, "/");
  const extension = path.extname(filePath);
  const fileName = path.basename(filePath, extension);
  const folderPath = path.dirname(relativePath).replace(/\\/g, "/");
  const topic = folderPath.split("/")[0] ?? "uncategorized";
  const sourceUrl = typeof data.source === "string" ? data.source : null;
  const authors = normalizeAuthor(data.author);
  const publishedAt = normalizeDate(data.published ?? data.date, filePath);

  return {
    id: createHash(relativePath),
    slug: relativePath.replace(/\.md$/i, ""),
    title: typeof data.title === "string" ? data.title.trim() : titleizeFilename(fileName),
    authors,
    authorLabel: authors.join(", ") || "Unknown",
    publishedAt,
    sourceUrl,
    topic,
    folderPath,
    fileName,
    relativePath,
  };
}

function loadExistingEntries() {
  if (!fs.existsSync(OUTPUT_PATH)) {
    return null;
  }

  try {
    return JSON.parse(fs.readFileSync(OUTPUT_PATH, "utf8"));
  } catch {
    return null;
  }
}

const entries = INCLUDED_TOPICS.flatMap((topic) => findMarkdownFiles(path.join(VAULT_ROOT, topic)).map(readEntry)).sort(
  (left, right) => new Date(right.publishedAt).getTime() - new Date(left.publishedAt).getTime(),
);

const nextEntries = entries.length > 0 ? entries : loadExistingEntries() ?? [];

fs.mkdirSync(path.dirname(OUTPUT_PATH), { recursive: true });
fs.writeFileSync(OUTPUT_PATH, `${JSON.stringify(nextEntries, null, 2)}\n`);

if (entries.length === 0 && nextEntries.length > 0) {
  console.log(`Vault source missing. Preserved ${nextEntries.length} committed entries at ${OUTPUT_PATH}`);
} else {
  console.log(`Generated ${nextEntries.length} vault entries at ${OUTPUT_PATH}`);
}
