/**
 * Generates public/ochoa-cv.pdf — terminal-aesthetic branded CV
 * Run: node scripts/gen-cv-pdf.mjs
 */
import PDFDocument from "pdfkit";
import { createWriteStream } from "fs";
import { fileURLToPath } from "url";
import { dirname, resolve } from "path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT = resolve(__dirname, "../public/ochoa-cv.pdf");

// ── Colours ─────────────────────────────────────────────────────────────────
const BG    = "#0a0a0a";
const FG    = "#e8e8e8";
const MUTED = "#888888";
const DIM   = "#3a3a3a";
const SOFT  = "#666666";

// ── CV data (mirrors config/cv.ts) ──────────────────────────────────────────
const profile = {
  name: "Andre Ochoa",
  title: "Founder · Product builder · Operator",
  bio: "Builder. Product leader turned indie founder. Shipping products with AI agent teams from Porto, Portugal.",
};

const experience = [
  { company: "BUILD.FUN.FREE",    role: "Founder",                          period: "Current",  summary: "Building products in public and using writing as both distribution and reflection." },
  { company: "Jscrambler",        role: "Developer security products",      period: "Previous", summary: "Worked on developer-facing security products with a strong bias toward clarity and practical outcomes." },
  { company: "knok",              role: "Digital health product work",      period: "Previous", summary: "Helped shape digital healthcare experiences in a fast-moving environment." },
  { company: "Critical TechWorks",role: "Product inside large systems",     period: "Previous", summary: "Developed product instincts inside a large-scale technology organization." },
  { company: "Sonae MC",          role: "Finance → operations → product",  period: "Earlier",  summary: "Started from the numbers side and learned how businesses really move underneath the narrative." },
];

const skills = [
  "Founder-led product strategy",
  "Product discovery and validation",
  "0-to-1 execution",
  "AI-assisted building workflows",
  "Writing in public",
  "Cross-functional communication",
  "Operational thinking",
];

const links = [
  { label: "Web",      value: "andochoa.com" },
  { label: "X",        value: "x.com/andochoa" },
  { label: "LinkedIn", value: "linkedin.com/in/andreochoa" },
  { label: "GitHub",   value: "github.com/AndOchoa" },
  { label: "Cal",      value: "cal.com/andochoa/chitchat" },
];

// ── Layout constants ─────────────────────────────────────────────────────────
const PW = 595.28;
const PH = 841.89;
const M  = 48;
const CW = PW - M * 2;

// ── Helpers ──────────────────────────────────────────────────────────────────
function dashedRect(doc, x, y, w, h, color = DIM) {
  doc.save().dash(2, { space: 3 }).rect(x, y, w, h).strokeColor(color).stroke().undash().restore();
}

function hline(doc, y, color = DIM) {
  doc.save().dash(2, { space: 3 }).moveTo(M, y).lineTo(PW - M, y).strokeColor(color).stroke().undash().restore();
}

function sectionLabel(doc, text, y) {
  doc.font("Courier").fontSize(7).fillColor(SOFT).text(text.toUpperCase(), M, y, { characterSpacing: 2, width: CW });
  return y + 16;
}

// ── Build ────────────────────────────────────────────────────────────────────
const doc = new PDFDocument({ size: "A4", margins: { top: 0, bottom: 0, left: 0, right: 0 } });
const stream = createWriteStream(OUT);
doc.pipe(stream);
const finished = new Promise((res, rej) => { stream.on("finish", res); stream.on("error", rej); });

// Background fill
doc.rect(0, 0, PW, PH).fill(BG);

let y = M;

// ── Header ───────────────────────────────────────────────────────────────────
doc.font("Courier-Bold").fontSize(20).fillColor(FG).text(profile.name, M, y, { width: CW });
y += 28;
doc.font("Courier").fontSize(8).fillColor(MUTED).text(profile.title, M, y, { width: CW, characterSpacing: 1 });
y += 14;
hline(doc, y);
y += 12;
doc.font("Courier").fontSize(9).fillColor(SOFT).text(profile.bio, M, y, { width: CW, lineGap: 3 });
y += 28;

// ── Experience ───────────────────────────────────────────────────────────────
y = sectionLabel(doc, "Experience", y);

for (const role of experience) {
  const boxX = M;
  const boxY = y;
  const innerX = boxX + 10;
  const innerW = CW - 20;

  // Role
  doc.font("Courier-Bold").fontSize(9).fillColor(FG).text(role.role, innerX, boxY + 8, { width: innerW - 70 });
  // Period (right side)
  doc.font("Courier").fontSize(7).fillColor(DIM).text(role.period.toUpperCase(), boxX + CW - 70, boxY + 10, { width: 60, align: "right", characterSpacing: 1 });
  // Company
  doc.font("Courier").fontSize(8).fillColor(MUTED).text(role.company, innerX, boxY + 22, { width: innerW });
  // Summary
  const summaryY = boxY + 35;
  doc.font("Courier").fontSize(8).fillColor(SOFT).text(role.summary, innerX, summaryY, { width: innerW, lineGap: 2 });

  // Calculate box height based on summary text
  const summaryLines = Math.ceil(role.summary.length / 72);
  const boxH = 35 + summaryLines * 12 + 10;

  dashedRect(doc, boxX, boxY, CW, boxH);
  y = boxY + boxH + 5;

  if (y > PH - 120) {
    doc.addPage();
    doc.rect(0, 0, PW, PH).fill(BG);
    y = M;
  }
}

y += 8;

// ── Skills ───────────────────────────────────────────────────────────────────
y = sectionLabel(doc, "Skills", y);

const pillW = 170;
const pillH = 17;
const pillGap = 5;
const pillCols = Math.floor(CW / (pillW + pillGap));

skills.forEach((skill, i) => {
  const col = i % pillCols;
  const row = Math.floor(i / pillCols);
  const px = M + col * (pillW + pillGap);
  const py = y + row * (pillH + pillGap);
  dashedRect(doc, px, py, pillW, pillH);
  doc.font("Courier").fontSize(7).fillColor(MUTED).text(skill, px + 6, py + 5, { width: pillW - 12 });
});

y += Math.ceil(skills.length / pillCols) * (pillH + pillGap) + 12;

// ── Education ────────────────────────────────────────────────────────────────
y = sectionLabel(doc, "Education", y);
dashedRect(doc, M, y, CW, 30);
doc.font("Courier-Bold").fontSize(8).fillColor(FG).text("Catolica Portuguesa University", M + 10, y + 8, { width: CW - 20 });
doc.font("Courier").fontSize(7).fillColor(MUTED).text("Economics and finance foundation", M + 10, y + 19, { width: CW - 20 });
y += 42;

// ── Contact ──────────────────────────────────────────────────────────────────
y = sectionLabel(doc, "Contact", y);

const lCols = 3;
const lW = Math.floor((CW - (lCols - 1) * pillGap) / lCols);
links.forEach((link, i) => {
  const col = i % lCols;
  const row = Math.floor(i / lCols);
  const px = M + col * (lW + pillGap);
  const py = y + row * (pillH + pillGap);
  dashedRect(doc, px, py, lW, pillH);
  doc
    .font("Courier-Bold").fontSize(6).fillColor(SOFT)
    .text(link.label.toUpperCase(), px + 6, py + 3, { continued: true, characterSpacing: 1 });
  doc
    .font("Courier").fontSize(6).fillColor(DIM)
    .text(`  ${link.value}`, { width: lW - 12 });
});

y += Math.ceil(links.length / lCols) * (pillH + pillGap) + 12;

// ── Footer ───────────────────────────────────────────────────────────────────
hline(doc, y);
y += 8;
doc.font("Courier").fontSize(6).fillColor(DIM).text("andochoa.com · BUILD.FUN.FREE · Porto, Portugal", M, y, { width: CW, align: "center", characterSpacing: 1 });

doc.end();
await finished;
console.log(`✓  PDF written → ${OUT}`);
