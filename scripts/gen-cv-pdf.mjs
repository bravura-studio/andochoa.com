/**
 * Generates public/ochoa-cv.pdf — clean branded CV, full text (flows across pages)
 * Run: node scripts/gen-cv-pdf.mjs
 */
import PDFDocument from "pdfkit";
import { createWriteStream, existsSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, resolve } from "path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT         = resolve(__dirname, "../public/ochoa-cv.pdf");
const PROFILE_PIC = resolve(__dirname, "../public/profile.jpg");

// ── Colours ──────────────────────────────────────────────────────────────────
const BG     = "#0a0a0a";
const FG     = "#e8e8e8";
const MUTED  = "#909090";
const DIM    = "#444444";
const SOFT   = "#666666";
const ACCENT = "#b0b0b0";

// ── CV data ───────────────────────────────────────────────────────────────────
const profile = {
  name:     "Andre Ochoa",
  title:    "Founder · Product builder · Operator",
  url:      "andochoa.com",
  location: "Porto, Portugal",
  bio:      "Builder with an economics background who crossed into product, code, and entrepreneurship. " +
            "Building products with AI agent teams. Writing about the process in public.",
};

const experience = [
  {
    company: "BUILD.FUN.FREE",
    role:    "Founder & Portfolio CEO",
    period:  "2025 — Present",
    summary: "Building a portfolio of products with AI-powered agent teams.",
    highlights: [
      "Shaping a portfolio around product strategy, AI leverage, and founder-led execution.",
      "Turning live work into essays, prompts, and operating principles that compound.",
    ],
  },
  {
    company: "Jscrambler",
    role:    "Product Leader",
    period:  "Dec 2023 — May 2024",
    summary: "Product vision, strategy and discovery. Shape Up method.",
    highlights: [
      "Balanced customer context, roadmap tradeoffs, and execution detail across cross-functional teams.",
      "Translated technical constraints into product decisions users could actually feel.",
    ],
  },
  {
    company: "knok",
    role:    "Senior Product Manager",
    period:  "Sep 2021 — Sep 2023",
    summary: "Product discovery & delivery. Upload times +50%, scheduling +20%.",
    highlights: [
      "Worked across operations, product delivery, and user needs where reliability mattered.",
      "Built comfort navigating ambiguity, stakeholder friction, and iterative product discovery.",
    ],
  },
  {
    company: "Critical TechWorks",
    role:    "Product Owner",
    period:  "Feb 2021 — Sep 2021",
    summary: "Data pipelines to AWS. Migrated 10TB+.",
    highlights: [
      "Operated close to engineering and learned where structure helps, and where it slows good work down.",
      "Strengthened the habit of turning messy inputs into concrete next steps.",
    ],
  },
  {
    company: "Sonae MC",
    role:    "Product Manager",
    period:  "Sep 2017 — Aug 2020",
    summary: "Analytical P&L model. +20% sales margin, -15% stock cost.",
    highlights: [
      "Built fluency in planning, operations, and commercial reality before moving deeper into product.",
      "Carried that operator lens forward into every later role.",
    ],
  },
];

const education = [
  {
    degree: "Master in Finance (17/20)",
    school: "Universidade Católica Portuguesa",
    period: "2009 — 2011",
  },
  {
    degree: "Economics",
    school: "Universidade Católica Portuguesa",
    period: "2004 — 2007",
  },
];

const skills = [
  "Founder-led product strategy",
  "Product discovery & validation",
  "0-to-1 execution",
  "AI-assisted building workflows",
  "Writing in public",
  "Cross-functional comms",
  "Operational thinking",
];

const links = [
  { label: "Web",      value: "andochoa.com" },
  { label: "X",        value: "x.com/andochoa" },
  { label: "LinkedIn", value: "linkedin.com/in/andreochoa" },
  { label: "GitHub",   value: "github.com/AndOchoa" },
  { label: "Cal",      value: "cal.com/andochoa/chitchat" },
];

// ── Layout ────────────────────────────────────────────────────────────────────
const PW     = 595.28;
const PH     = 841.89;
const M      = 44;
const CW     = PW - M * 2;
const PIC_SZ = 68;

const FOOTER_H = 26;            // reserved strip at the bottom of every page
const BOTTOM   = PH - M - FOOTER_H;

// ── Helpers ───────────────────────────────────────────────────────────────────
function hline(doc, y, color = DIM) {
  doc.save().moveTo(M, y).lineTo(PW - M, y).strokeColor(color).lineWidth(0.4).stroke().restore();
}

function accentBar(doc, x, y, h, color = SOFT) {
  doc.save().rect(x, y, 2, h).fill(color).restore();
}

function sectionLabel(doc, text, y) {
  doc.font("Courier").fontSize(6.5).fillColor(SOFT)
     .text(text.toUpperCase(), M, y, { characterSpacing: 2, width: CW });
  return y + 13;
}

// ── Build ─────────────────────────────────────────────────────────────────────
const doc    = new PDFDocument({
  size: "A4",
  margins: { top: 0, bottom: 0, left: 0, right: 0 },
  bufferPages: true,
});
const stream = createWriteStream(OUT);
doc.pipe(stream);
const finished = new Promise((res, rej) => { stream.on("finish", res); stream.on("error", rej); });

function paintBackground() {
  doc.rect(0, 0, PW, PH).fill(BG);
}

function newPage() {
  doc.addPage();
  paintBackground();
  return M;
}

/** Returns a y that has `h` points of room left above the footer, adding a page if needed. */
function ensureSpace(y, h) {
  return y + h > BOTTOM ? newPage() : y;
}

paintBackground();

let y = M;

// ── Header ────────────────────────────────────────────────────────────────────
const picX  = PW - M - PIC_SZ;
const textW = CW - PIC_SZ - 16;

// Profile pic (colour — circular clip)
if (existsSync(PROFILE_PIC)) {
  const cx = picX + PIC_SZ / 2;
  const cy = y + PIC_SZ / 2;
  const r  = PIC_SZ / 2;
  doc.save().circle(cx, cy, r).clip();
  doc.image(PROFILE_PIC, picX, y, { width: PIC_SZ, height: PIC_SZ });
  doc.restore();
  // Subtle border
  doc.save().circle(cx, cy, r).strokeColor(DIM).lineWidth(0.6).stroke().restore();
}

doc.font("Courier-Bold").fontSize(20).fillColor(FG)
   .text(profile.name, M, y, { width: textW });
y += 26;

doc.font("Courier").fontSize(8).fillColor(MUTED)
   .text(profile.title, M, y, { width: textW, characterSpacing: 0.5 });
y += 13;

doc.font("Courier-Bold").fontSize(8).fillColor(ACCENT)
   .text(profile.url, M, y, { width: textW });
y += 13;

doc.font("Courier").fontSize(7.5).fillColor(SOFT)
   .text(profile.bio, M, y, { width: textW, lineGap: 2 });
y += 24;

// Ensure content clears the profile pic
y = Math.max(y, M + PIC_SZ + 10);

hline(doc, y);
y += 10;

// ── Experience ────────────────────────────────────────────────────────────────
y = sectionLabel(doc, "Experience", y);

const iX = M + 8;
const iW = CW - 8;
const bX = iX + 8;
const bW = iW - 8;

for (const exp of experience) {
  // Measure the whole entry first so the accent bar and page break match it.
  doc.font("Courier-Bold").fontSize(8.5);
  const roleH = doc.heightOfString(exp.role, { width: iW - 84 });

  const summaryText = `${exp.company}  ·  ${exp.summary}`;
  doc.font("Courier").fontSize(7.5);
  const summaryH = doc.heightOfString(summaryText, { width: iW, lineGap: 1 });

  doc.font("Courier").fontSize(7);
  const bulletHs = exp.highlights.map((h) => doc.heightOfString(h, { width: bW, lineGap: 1.5 }));
  const bulletsH = bulletHs.reduce((acc, h) => acc + h + 3, 0);

  const entryH = roleH + 3 + summaryH + (bulletsH ? bulletsH + 2 : 0);

  y = ensureSpace(y, entryH);
  accentBar(doc, M, y, entryH);

  doc.font("Courier-Bold").fontSize(8.5).fillColor(FG)
     .text(exp.role, iX, y, { width: iW - 84 });
  doc.font("Courier").fontSize(6.5).fillColor(DIM)
     .text(exp.period, M + CW - 82, y + 1, { width: 82, align: "right" });

  let ey = y + roleH + 3;
  doc.font("Courier").fontSize(7.5).fillColor(MUTED)
     .text(summaryText, iX, ey, { width: iW, lineGap: 1 });
  ey += summaryH + (bulletsH ? 2 : 0);

  exp.highlights.forEach((h, i) => {
    doc.save().circle(iX + 2.5, ey + 3.5, 0.9).fill(SOFT).restore();
    doc.font("Courier").fontSize(7).fillColor(SOFT)
       .text(h, bX, ey, { width: bW, lineGap: 1.5 });
    ey += bulletHs[i] + 3;
  });

  y += entryH + 8;
}

y = ensureSpace(y, 20);
hline(doc, y);
y += 10;

// ── Skills ────────────────────────────────────────────────────────────────────
const SCOLS = 4;
const sColW = Math.floor((CW - (SCOLS - 1) * 6) / SCOLS);
const sRowH = 15;
const skillsH = Math.ceil(skills.length / SCOLS) * sRowH;

y = ensureSpace(y, 13 + skillsH);
y = sectionLabel(doc, "Skills", y);

skills.forEach((s, i) => {
  const col = i % SCOLS;
  const row = Math.floor(i / SCOLS);
  const px  = M + col * (sColW + 6);
  const py  = y + row * sRowH;
  doc.font("Courier").fontSize(7).fillColor(MUTED).text(s, px, py, { width: sColW });
});

y += skillsH + 10;
y = ensureSpace(y, 20);
hline(doc, y);
y += 10;

// ── Education ─────────────────────────────────────────────────────────────────
y = ensureSpace(y, 13 + 28);
y = sectionLabel(doc, "Education", y);

for (const edu of education) {
  const entryH = 22;
  y = ensureSpace(y, entryH + 6);
  accentBar(doc, M, y, entryH - 2);

  doc.font("Courier-Bold").fontSize(8).fillColor(FG)
     .text(edu.degree, M + 8, y, { width: CW - 90 });
  doc.font("Courier").fontSize(6.5).fillColor(DIM)
     .text(edu.period, M + CW - 82, y + 1, { width: 82, align: "right" });
  doc.font("Courier").fontSize(7.5).fillColor(MUTED)
     .text(edu.school, M + 8, y + 12, { width: CW - 8 });

  y += entryH + 6;
}

y = ensureSpace(y, 20);
hline(doc, y);
y += 10;

// ── Contact ───────────────────────────────────────────────────────────────────
y = ensureSpace(y, 13 + 22);
y = sectionLabel(doc, "Contact", y);

const LCOLS = links.length;
const lColW = Math.floor((CW - (LCOLS - 1) * 8) / LCOLS);

links.forEach((lnk, i) => {
  const px = M + i * (lColW + 8);
  doc.font("Courier-Bold").fontSize(6).fillColor(SOFT)
     .text(lnk.label.toUpperCase(), px, y, { characterSpacing: 1 });
  doc.font("Courier").fontSize(7).fillColor(DIM)
     .text(lnk.value, px, y + 9, { width: lColW });
});

// ── Footer (every page) ───────────────────────────────────────────────────────
const { start, count } = doc.bufferedPageRange();

for (let i = start; i < start + count; i += 1) {
  doc.switchToPage(i);
  const fy = PH - M - FOOTER_H + 6;
  hline(doc, fy);
  doc.font("Courier").fontSize(6).fillColor(DIM)
     .text(
       count > 1
         ? `${profile.url}  ·  BUILD.FUN.FREE  ·  ${profile.location}  ·  ${i - start + 1}/${count}`
         : `${profile.url}  ·  BUILD.FUN.FREE  ·  ${profile.location}`,
       M, fy + 7, { width: CW, align: "center", characterSpacing: 1 }
     );
}

doc.flushPages();
doc.end();
await finished;
console.log(`✓  PDF written → ${OUT} (${count} page${count > 1 ? "s" : ""})`);
