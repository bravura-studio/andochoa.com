/**
 * Generates public/ochoa-cv.pdf — clean branded CV, one page
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
  },
  {
    company: "Jscrambler",
    role:    "Product Leader",
    period:  "Dec 2023 — May 2024",
    summary: "Product vision, strategy and discovery. Shape Up method.",
  },
  {
    company: "knok",
    role:    "Senior Product Manager",
    period:  "Sep 2021 — Sep 2023",
    summary: "Product discovery & delivery. Upload times +50%, scheduling +20%.",
  },
  {
    company: "Critical TechWorks",
    role:    "Product Owner",
    period:  "Feb 2021 — Sep 2021",
    summary: "Data pipelines to AWS. Migrated 10TB+.",
  },
  {
    company: "Sonae MC",
    role:    "Product Manager",
    period:  "Sep 2017 — Aug 2020",
    summary: "Analytical P&L model. +20% sales margin, -15% stock cost.",
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
const doc    = new PDFDocument({ size: "A4", margins: { top: 0, bottom: 0, left: 0, right: 0 } });
const stream = createWriteStream(OUT);
doc.pipe(stream);
const finished = new Promise((res, rej) => { stream.on("finish", res); stream.on("error", rej); });

// Background
doc.rect(0, 0, PW, PH).fill(BG);

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

for (const exp of experience) {
  const entryH = 30;
  accentBar(doc, M, y, entryH - 2);

  const iX = M + 8;
  const iW = CW - 8;

  doc.font("Courier-Bold").fontSize(8.5).fillColor(FG)
     .text(exp.role, iX, y, { width: iW - 84 });
  doc.font("Courier").fontSize(6.5).fillColor(DIM)
     .text(exp.period, M + CW - 82, y + 1, { width: 82, align: "right" });
  doc.font("Courier").fontSize(7.5).fillColor(MUTED)
     .text(`${exp.company}  ·  ${exp.summary}`, iX, y + 13, { width: iW, lineGap: 1 });

  y += entryH + 4;
}

hline(doc, y);
y += 10;

// ── Skills ────────────────────────────────────────────────────────────────────
y = sectionLabel(doc, "Skills", y);

const SCOLS = 4;
const sColW = Math.floor((CW - (SCOLS - 1) * 6) / SCOLS);
const sRowH = 15;

skills.forEach((s, i) => {
  const col = i % SCOLS;
  const row = Math.floor(i / SCOLS);
  const px  = M + col * (sColW + 6);
  const py  = y + row * sRowH;
  doc.font("Courier").fontSize(7).fillColor(MUTED).text(s, px, py, { width: sColW });
});

y += Math.ceil(skills.length / SCOLS) * sRowH + 10;
hline(doc, y);
y += 10;

// ── Education ─────────────────────────────────────────────────────────────────
y = sectionLabel(doc, "Education", y);

for (const edu of education) {
  const entryH = 22;
  accentBar(doc, M, y, entryH - 2);

  doc.font("Courier-Bold").fontSize(8).fillColor(FG)
     .text(edu.degree, M + 8, y, { width: CW - 90 });
  doc.font("Courier").fontSize(6.5).fillColor(DIM)
     .text(edu.period, M + CW - 82, y + 1, { width: 82, align: "right" });
  doc.font("Courier").fontSize(7.5).fillColor(MUTED)
     .text(edu.school, M + 8, y + 12, { width: CW - 8 });

  y += entryH + 6;
}

hline(doc, y);
y += 10;

// ── Contact ───────────────────────────────────────────────────────────────────
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

y += 26;

// ── Footer ────────────────────────────────────────────────────────────────────
hline(doc, y);
y += 7;
doc.font("Courier").fontSize(6).fillColor(DIM)
   .text(
     `${profile.url}  ·  BUILD.FUN.FREE  ·  ${profile.location}`,
     M, y, { width: CW, align: "center", characterSpacing: 1 }
   );

doc.end();
await finished;
console.log(`✓  PDF written → ${OUT}`);
