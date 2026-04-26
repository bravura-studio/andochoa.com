import Image from "next/image";
import Link from "next/link";
import { CalendarDays, Download } from "lucide-react";
import { SiteShell } from "@/components/site-shell";
import { cvEducation, cvExperience, cvLinks, cvProfile, cvSkills } from "@/config/cv";
import { buildPageMetadata } from "@/lib/site";

const outlineSections = [
  { id: "bio", label: "Bio" },
  { id: "mantra", label: "Mantra" },
  { id: "experience", label: "Experience" },
  { id: "education", label: "Education" },
  { id: "skills", label: "Skills" },
  { id: "contact", label: "Contact" },
];

export const metadata = buildPageMetadata({
  title: "About",
  description: "Background, experience, and founder profile for Andre Ochoa.",
  path: "/about",
});

export default function AboutPage() {
  return (
    <SiteShell
      activityKey="about"
      breadcrumbs={[{ label: "andochoa.com", href: "/" }, { label: "about.md" }]}
      sidebar={
        <div className="space-y-5">
          <div className="space-y-1">
            {outlineSections.map((section) => (
              <a
                className="block rounded-md px-3 py-2 text-[12px] text-white/40 transition hover:bg-white/[0.04] hover:text-white/76"
                href={`#${section.id}`}
                key={section.id}
              >
                {section.label}
              </a>
            ))}
          </div>

          <div className="space-y-2 border-t border-white/7 pt-4">
            <a
              className="flex items-center justify-center gap-2 rounded-md border border-dashed border-white/12 bg-white/[0.03] px-3 py-3 text-[11px] uppercase tracking-[0.18em] text-white/70 transition hover:bg-white/[0.06]"
              download
              href="/ochoa-cv.pdf"
            >
              <Download className="h-4 w-4" />
              Download CV
            </a>
            <Link
              className="flex items-center justify-center gap-2 rounded-md border border-dashed border-white/12 bg-white/[0.03] px-3 py-3 text-[11px] uppercase tracking-[0.18em] text-white/70 transition hover:bg-white/[0.06]"
              href="https://cal.com/andochoa/chitchat"
              rel="noreferrer"
              target="_blank"
            >
              <CalendarDays className="h-4 w-4" />
              Book a call
            </Link>
          </div>
        </div>
      }
      sidebarTitle="outline"
      statusMeta="about.md · 6 sections"
      tabs={[{ active: true, label: "about.md" }]}
    >
      <article className="mx-auto max-w-[760px] space-y-8">
        <section className="shell-card p-5 sm:p-6" id="bio">
          <div className="flex flex-col gap-5 sm:flex-row sm:items-center">
            <div className="relative h-20 w-20 overflow-hidden rounded-full border border-dashed border-white/14 bg-black/40">
              <Image alt="Andre Ochoa portrait" className="object-cover grayscale" fill priority sizes="80px" src="/profile.jpg" />
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
          <p className="text-[10px] uppercase tracking-[0.3em] text-white/28">build.fun.free</p>
          <p className="mt-4 text-[14px] leading-8 text-white/64">{cvProfile.summary}</p>
        </section>

        <section id="experience">
          <p className="mb-4 text-[10px] uppercase tracking-[0.3em] text-white/28">experience</p>
          <div className="space-y-3">
            {cvExperience.map((role) => (
              <article className="shell-card p-5" key={`${role.company}-${role.role}`}>
                <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <h2 className="text-[16px] text-white">{role.role}</h2>
                    <p className="mt-1 text-[12px] text-white/38">{role.company}</p>
                  </div>
                  <p className="text-[10px] uppercase tracking-[0.2em] text-white/28">{role.period}</p>
                </div>
                <p className="mt-4 text-[13px] leading-7 text-white/54">{role.summary}</p>
              </article>
            ))}
          </div>
        </section>

        <section id="education">
          <p className="mb-4 text-[10px] uppercase tracking-[0.3em] text-white/28">education</p>
          <div className="space-y-3">
            {cvEducation.items.map((item) => (
              <article className="shell-card p-5" key={item}>
                <p className="text-[14px] text-white">{item}</p>
                <p className="mt-2 text-[11px] uppercase tracking-[0.2em] text-white/28">{cvEducation.title}</p>
              </article>
            ))}
          </div>
        </section>

        <section id="skills">
          <p className="mb-4 text-[10px] uppercase tracking-[0.3em] text-white/28">skills</p>
          <div className="flex flex-wrap gap-2">
            {cvSkills.items.map((skill) => (
              <span className="rounded-md border border-dashed border-white/12 px-3 py-2 text-[12px] text-white/56" key={skill}>
                {skill}
              </span>
            ))}
          </div>
        </section>

        <section className="shell-card p-5 sm:p-6" id="contact">
          <p className="text-[10px] uppercase tracking-[0.3em] text-white/28">contact</p>
          <div className="mt-4 space-y-2">
            {cvLinks.map((link) => (
              <Link
                className="flex items-center justify-between gap-3 rounded-md border border-dashed border-white/10 bg-black/25 px-3 py-3 text-[12px] text-white/62 transition hover:bg-white/[0.04] hover:text-white"
                href={link.href}
                key={link.href}
                rel="noreferrer"
                target="_blank"
              >
                <span>{link.label}</span>
                <span className="text-white/34">{link.value}</span>
              </Link>
            ))}
          </div>
        </section>
      </article>
    </SiteShell>
  );
}
