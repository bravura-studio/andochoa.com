import Image from "next/image";
import Link from "next/link";
import { CalendarDays, Download } from "lucide-react";
import { cvEducation, cvExperience, cvProfile } from "@/config/cv";
import { buildPageMetadata } from "@/lib/site";

export const metadata = buildPageMetadata({
  title: "About",
  description: "Background, experience, and founder profile for Andre Ochoa.",
  path: "/about",
});

export default function AboutPage() {
  return (
    <section className="mx-auto max-w-[680px] rounded-[1.5rem] border border-dashed border-white/10 bg-white/[0.03] p-5 shadow-terminal backdrop-blur-xl sm:p-8">
      <p className="text-[10px] uppercase tracking-[0.32em] text-white/38">about</p>

      <header className="mt-6 flex flex-col items-start gap-5 sm:flex-row sm:items-center">
        <div className="relative h-24 w-24 overflow-hidden rounded-full border border-dashed border-white/14 bg-black/40">
          <Image
            alt="Andre Ochoa portrait"
            className="object-cover grayscale contrast-110"
            fill
            priority
            sizes="96px"
            src="/profile.jpg"
          />
        </div>

        <div>
          <h1 className="text-2xl font-bold text-white">{cvProfile.name}</h1>
          <p className="mt-2 text-[13px] text-white/48">{cvProfile.title}</p>
        </div>
      </header>

      <div className="mt-8 space-y-5">
        {cvProfile.bio.map((paragraph) => (
          <p className="text-[14px] leading-[1.8] text-white/70" key={paragraph}>
            {paragraph}
          </p>
        ))}
      </div>

      <div className="mt-6 rounded-2xl border border-dashed border-white/12 bg-black/25 p-5">
        <p className="text-[11px] uppercase tracking-[0.34em] text-white/42">BUILD · FUN · FREE</p>
        <p className="mt-3 text-[14px] leading-[1.8] text-white/68">{cvProfile.summary}</p>
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        <a
          className="inline-flex items-center gap-2 rounded-full border border-dashed border-white/14 bg-white/[0.03] px-4 py-3 text-sm text-white/80 transition hover:border-white/22 hover:bg-white/[0.07]"
          download
          href="/ochoa-cv.pdf"
        >
          <Download className="h-4 w-4" />
          Download CV
        </a>
        <Link
          className="inline-flex items-center gap-2 rounded-full border border-dashed border-white/14 bg-white/[0.03] px-4 py-3 text-sm text-white/80 transition hover:border-white/22 hover:bg-white/[0.07]"
          href="https://cal.com/andochoa/chitchat"
          rel="noreferrer"
          target="_blank"
        >
          <CalendarDays className="h-4 w-4" />
          Book a Call
        </Link>
      </div>

      <div className="mt-10 space-y-8">
        <section>
          <div className="border-b border-dashed border-white/10 pb-3">
            <p className="text-[10px] uppercase tracking-[0.3em] text-white/42">&gt; experience</p>
          </div>

          <div className="mt-4 space-y-3">
            {cvExperience.map((role) => (
              <article
                className="rounded-2xl border border-dashed border-white/12 bg-black/25 p-4"
                key={`${role.company}-${role.role}`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h2 className="text-[14px] font-semibold text-white">{role.role}</h2>
                    <p className="mt-1 text-[12px] text-white/48">{role.company}</p>
                  </div>
                  <p className="text-right text-[11px] text-white/40">{role.period}</p>
                </div>
                <p className="mt-3 text-[12px] leading-6 text-white/58">{role.summary}</p>
              </article>
            ))}
          </div>
        </section>

        <section>
          <div className="border-b border-dashed border-white/10 pb-3">
            <p className="text-[10px] uppercase tracking-[0.3em] text-white/42">&gt; education</p>
          </div>

          <div className="mt-4 space-y-3">
            {cvEducation.items.map((item) => (
              <article className="rounded-2xl border border-dashed border-white/12 bg-black/25 p-4" key={item}>
                <h2 className="text-[14px] font-semibold text-white">{item}</h2>
                <p className="mt-2 text-[12px] text-white/48">{cvEducation.title}</p>
              </article>
            ))}
          </div>
        </section>
      </div>
    </section>
  );
}
