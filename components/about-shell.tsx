"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { CalendarDays, Download, Github, Linkedin, Twitter } from "lucide-react";
import { SiteShell } from "@/components/site-shell";
import { ExperienceTimeline } from "@/components/experience-timeline";
import { AboutSidebar } from "@/components/about-sidebar";
import { BackToTop } from "@/components/back-to-top";
import { cvEducation, cvExperience, cvLinks, cvProfile, cvSkills } from "@/config/cv";

const socialIconMap: Record<string, React.ReactNode> = {
  X: <Twitter className="h-4 w-4" />,
  LinkedIn: <Linkedin className="h-4 w-4" />,
  GitHub: <Github className="h-4 w-4" />,
};

const socialLinks = cvLinks.filter((l) => l.label in socialIconMap);

const mantraColumns = [
  { word: "BUILD", line1: "Ship what", line2: "matters" },
  { word: "FUN", line1: "Enjoy the", line2: "journey" },
  { word: "FREE", line1: "Own your", line2: "time" },
];

export function AboutShell() {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  return (
    <SiteShell
      activityKey="about"
      breadcrumbs={[{ label: "andochoa.com", href: "/" }, { label: "about.md" }]}
      mobileSidebarOpen={mobileSidebarOpen}
      onMobileSidebarOpenChange={setMobileSidebarOpen}
      sidebar={<AboutSidebar onSectionClick={() => setMobileSidebarOpen(false)} />}
      sidebarTitle="about.md"
      statusMeta="about.md · 6 sections"
      tabs={[{ active: true, label: "about.md" }]}
    >
      <article className="mx-auto max-w-[760px] space-y-8">
        <section className="shell-card p-5 sm:p-6" id="bio">
          <div className="flex flex-col gap-5 sm:flex-row sm:items-center">
            <div className="relative h-20 w-20 overflow-hidden rounded-full border border-dashed border-white/14 bg-black/40">
              <Image alt="Andre Ochoa portrait" className="object-cover" fill priority sizes="80px" src="/profile.jpg" />
            </div>
            <div>
              <h1 className="text-[28px] font-semibold tracking-[-0.04em] text-white">{cvProfile.name}</h1>
              <p className="mt-2 text-[12px] uppercase tracking-[0.24em] text-white/32">{cvProfile.title}</p>
            </div>
          </div>

          <div className="mt-6 space-y-4">
            {cvProfile.bio.map((paragraph) => (
              <p className="text-[14px] leading-8 text-white/64" key={paragraph}>
                {paragraph}
              </p>
            ))}
          </div>
        </section>

        <section className="shell-card p-5 sm:p-6" id="mantra">
          <p className="mb-5 text-[10px] uppercase tracking-[0.3em] text-white/28">build·fun·free</p>
          <div className="grid grid-cols-3 gap-3">
            {mantraColumns.map((col) => (
              <div
                className="flex flex-col items-center rounded-md border border-dashed border-white/12 bg-white/[0.02] p-4 text-center backdrop-blur-md"
                key={col.word}
              >
                <p className="text-[22px] font-semibold tracking-[-0.02em] text-white sm:text-[26px]">{col.word}</p>
                <p className="mt-2 text-[11px] leading-5 text-white/38">
                  {col.line1}
                  <br />
                  {col.line2}
                </p>
              </div>
            ))}
          </div>
        </section>

        <section className="shell-card p-5 sm:p-6" id="experience">
          <p className="mb-5 text-[10px] uppercase tracking-[0.3em] text-white/28">experience</p>
          <ExperienceTimeline entries={cvExperience} />
        </section>

        <section className="shell-card p-5 sm:p-6" id="education">
          <p className="mb-5 text-[10px] uppercase tracking-[0.3em] text-white/28">education</p>
          <div className="space-y-3">
            {cvEducation.items.map((item) => (
              <div className="rounded-md border border-dashed border-white/10 bg-black/20 p-4" key={item}>
                <p className="text-[14px] text-white">{item}</p>
                <p className="mt-2 text-[11px] uppercase tracking-[0.2em] text-white/28">{cvEducation.title}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="shell-card p-5 sm:p-6" id="skills">
          <p className="mb-5 text-[10px] uppercase tracking-[0.3em] text-white/28">skills</p>
          <div className="flex flex-wrap gap-2">
            {cvSkills.items.map((skill) => (
              <span
                className="rounded-md border border-white/8 bg-white/[0.04] px-2.5 py-1 text-[9px] uppercase tracking-[0.18em] text-white/45"
                key={skill}
              >
                {skill}
              </span>
            ))}
          </div>
        </section>

        <section className="shell-card p-5 sm:p-6" id="contact">
          <p className="mb-5 text-[10px] uppercase tracking-[0.3em] text-white/28">contact</p>

          <div className="grid grid-cols-2 gap-3">
            <Link
              className="flex items-center justify-center gap-2 rounded-md border border-dashed border-white/18 bg-white/[0.04] px-4 py-3.5 text-[12px] uppercase tracking-[0.18em] text-white/80 transition hover:bg-white/[0.08] hover:text-white"
              href="https://cal.com/andochoa/chitchat"
              rel="noreferrer"
              target="_blank"
            >
              <CalendarDays className="h-4 w-4" />
              Book a Call →
            </Link>
            <a
              className="flex items-center justify-center gap-2 rounded-md border border-dashed border-white/18 bg-white/[0.04] px-4 py-3.5 text-[12px] uppercase tracking-[0.18em] text-white/80 transition hover:bg-white/[0.08] hover:text-white"
              download
              href="/ochoa-cv.pdf"
            >
              <Download className="h-4 w-4" />
              Download CV →
            </a>
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            {socialLinks.map((link) => (
              <Link
                className="flex items-center gap-2 rounded-md border border-dashed border-white/10 bg-black/20 px-3 py-2 text-[11px] text-white/50 transition hover:bg-white/[0.06] hover:text-white/80"
                href={link.href}
                key={link.href}
                rel="noreferrer"
                target="_blank"
              >
                {socialIconMap[link.label]}
                <span>{link.value}</span>
              </Link>
            ))}
          </div>
        </section>
      </article>
      <BackToTop triggerSectionId="bio" />
    </SiteShell>
  );
}
