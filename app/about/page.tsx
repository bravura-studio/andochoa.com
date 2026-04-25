import Image from "next/image";
import Link from "next/link";
import { ArrowUpRight, CalendarDays, Download, Github, Linkedin, Twitter } from "lucide-react";
import { cvEducation, cvExperience, cvLinks, cvProfile, cvSkills } from "@/config/cv";
import { buildPageMetadata } from "@/lib/site";

const socialIcons = {
  X: Twitter,
  LinkedIn: Linkedin,
  GitHub: Github,
  "Cal.com": CalendarDays,
} as const;

export const metadata = buildPageMetadata({
  title: "About",
  description: "Background, experience, and founder profile for Andre Ochoa.",
  path: "/about",
});

export default function AboutPage() {
  return (
    <div className="space-y-6">
      <section className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <div className="rounded-[2rem] border border-dashed border-white/15 bg-white/[0.05] p-6 shadow-terminal backdrop-blur-xl sm:p-8">
          <p className="text-xs uppercase tracking-[0.35em] text-white/42">about / founder file</p>
          <div className="mt-6 flex flex-col gap-6 lg:flex-row lg:items-start">
            <div className="relative h-40 w-40 shrink-0 overflow-hidden rounded-[2rem] border border-dashed border-white/16 bg-black/40 sm:h-48 sm:w-48">
              <Image
                alt="Andre Ochoa portrait"
                className="object-cover grayscale contrast-110"
                fill
                priority
                sizes="(min-width: 640px) 192px, 160px"
                src="/profile.jpg"
              />
            </div>
            <div className="min-w-0">
              <h1 className="text-3xl font-semibold tracking-[-0.05em] text-white sm:text-5xl">{cvProfile.name}</h1>
              <p className="mt-4 text-sm uppercase tracking-[0.28em] text-white/42">{cvProfile.title}</p>
              <p className="mt-5 max-w-2xl text-sm leading-7 text-white/62 sm:text-base">{cvProfile.summary}</p>
            </div>
          </div>

          <div className="mt-8 grid gap-4">
            {cvProfile.bio.map((paragraph) => (
              <p className="max-w-3xl text-sm leading-7 text-white/64 sm:text-base" key={paragraph}>
                {paragraph}
              </p>
            ))}
          </div>
        </div>

        <div className="rounded-[2rem] border border-dashed border-white/15 bg-white/[0.045] p-6 shadow-terminal backdrop-blur-xl sm:p-8">
          <div className="rounded-[1.75rem] border border-dashed border-white/12 bg-black/35 p-5">
            <p className="text-[11px] uppercase tracking-[0.4em] text-white/38">build.fun.free</p>
            <div className="mt-5 grid gap-3 sm:grid-cols-3">
              <div className="rounded-[1.4rem] border border-dashed border-white/12 bg-white/[0.04] p-4">
                <p className="text-xs uppercase tracking-[0.3em] text-white/35">build</p>
                <p className="mt-3 text-sm leading-6 text-white/68">
                  Turn ideas into products, notes, systems, and experiments that can survive contact with reality.
                </p>
              </div>
              <div className="rounded-[1.4rem] border border-dashed border-white/12 bg-white/[0.04] p-4">
                <p className="text-xs uppercase tracking-[0.3em] text-white/35">fun</p>
                <p className="mt-3 text-sm leading-6 text-white/68">
                  Chase work that creates energy instead of draining it. Joy is a strategy constraint, not a luxury.
                </p>
              </div>
              <div className="rounded-[1.4rem] border border-dashed border-white/12 bg-white/[0.04] p-4">
                <p className="text-xs uppercase tracking-[0.3em] text-white/35">free</p>
                <p className="mt-3 text-sm leading-6 text-white/68">
                  Use products and writing to buy back schedule, focus, and the right to choose what matters next.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            <Link
              className="inline-flex items-center justify-center gap-2 rounded-[1.4rem] border border-dashed border-white/16 bg-white px-4 py-4 text-sm font-medium text-black transition hover:bg-white/90"
              href="/ochoa-cv.pdf"
            >
              <Download className="h-4 w-4" />
              download background pdf
            </Link>
            <Link
              className="inline-flex items-center justify-center gap-2 rounded-[1.4rem] border border-dashed border-white/16 bg-white/[0.04] px-4 py-4 text-sm font-medium text-white/82 transition hover:border-white/24 hover:bg-white/[0.08]"
              href="https://cal.com/andochoa/chitchat"
              rel="noreferrer"
              target="_blank"
            >
              <CalendarDays className="h-4 w-4" />
              book a chat
            </Link>
          </div>

          <div className="mt-6 rounded-[1.75rem] border border-dashed border-white/12 bg-black/30 p-5">
            <p className="text-[11px] uppercase tracking-[0.38em] text-white/38">connect</p>
            <div className="mt-5 grid gap-3">
              {cvLinks.map((link) => {
                const Icon = socialIcons[link.label as keyof typeof socialIcons];

                return (
                  <Link
                    className="flex items-center justify-between gap-3 rounded-[1.2rem] border border-dashed border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-white/72 transition hover:border-white/20 hover:bg-white/[0.06] hover:text-white"
                    href={link.href}
                    key={link.href}
                    rel="noreferrer"
                    target="_blank"
                  >
                    <span className="inline-flex items-center gap-3">
                      <Icon className="h-4 w-4 text-white/48" />
                      <span>{link.label}</span>
                    </span>
                    <span className="inline-flex items-center gap-2 text-white/45">
                      {link.value}
                      <ArrowUpRight className="h-4 w-4" />
                    </span>
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      <section className="rounded-[2rem] border border-dashed border-white/15 bg-white/[0.045] p-6 shadow-terminal backdrop-blur-xl sm:p-8">
        <div className="flex flex-col gap-3 border-b border-dashed border-white/12 pb-6 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-white/42">selected work / operating history</p>
            <h2 className="mt-4 text-2xl font-semibold tracking-[-0.04em] text-white sm:text-3xl">
              Builder-first experience, not corporate theater.
            </h2>
          </div>
          <p className="max-w-xl text-sm leading-7 text-white/56">
            A condensed operating profile spanning finance, product, and founder work. Enough context to understand the
            path, without pretending the story is finished.
          </p>
        </div>

        <div className="mt-6 grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
          <div className="space-y-4">
            {cvExperience.map((role) => (
              <article
                className="rounded-[1.6rem] border border-dashed border-white/12 bg-black/30 p-5"
                key={`${role.company}-${role.role}`}
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p className="text-xs uppercase tracking-[0.28em] text-white/38">{role.company}</p>
                    <h3 className="mt-3 text-xl font-medium text-white">{role.role}</h3>
                  </div>
                  <span className="rounded-full border border-dashed border-white/14 px-3 py-1 text-[11px] uppercase tracking-[0.24em] text-white/45">
                    {role.period}
                  </span>
                </div>
                <p className="mt-4 text-sm leading-7 text-white/62">{role.summary}</p>
                <ul className="mt-4 space-y-2 text-sm leading-6 text-white/54">
                  {role.highlights.map((highlight) => (
                    <li className="flex gap-3" key={highlight}>
                      <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-white/45" />
                      <span>{highlight}</span>
                    </li>
                  ))}
                </ul>
              </article>
            ))}
          </div>

          <div className="space-y-4">
            <section className="rounded-[1.6rem] border border-dashed border-white/12 bg-black/30 p-5">
              <p className="text-xs uppercase tracking-[0.28em] text-white/38">{cvEducation.title}</p>
              <div className="mt-4 space-y-3">
                {cvEducation.items.map((item) => (
                  <p className="rounded-[1.2rem] border border-dashed border-white/10 bg-white/[0.03] px-4 py-4 text-sm leading-6 text-white/64" key={item}>
                    {item}
                  </p>
                ))}
              </div>
            </section>

            <section className="rounded-[1.6rem] border border-dashed border-white/12 bg-black/30 p-5">
              <p className="text-xs uppercase tracking-[0.28em] text-white/38">{cvSkills.title}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {cvSkills.items.map((skill) => (
                  <span
                    className="rounded-full border border-dashed border-white/12 bg-white/[0.03] px-3 py-2 text-sm text-white/66"
                    key={skill}
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </section>

            <section className="rounded-[1.6rem] border border-dashed border-white/12 bg-white/[0.03] p-5">
              <p className="text-xs uppercase tracking-[0.28em] text-white/38">availability</p>
              <p className="mt-4 text-sm leading-7 text-white/60">
                Open to founder conversations, builder-to-builder exchanges, and collaborations that fit the
                build-in-public rhythm.
              </p>
              <p className="mt-4 text-sm text-white/48">Base: {cvProfile.location}</p>
            </section>
          </div>
        </div>
      </section>
    </div>
  );
}
