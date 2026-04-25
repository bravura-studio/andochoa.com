import Link from "next/link";
import { cv } from "@/config/cv";
import { projects } from "@/config/projects";

export default function AboutPage() {
  return (
    <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
      <section className="rounded-[2rem] border border-border/80 bg-card/80 p-6 shadow-terminal sm:p-8">
        <p className="text-xs uppercase tracking-[0.35em] text-primary">about the founder</p>
        <h1 className="mt-4 text-3xl font-semibold">{cv.title}</h1>
        <p className="mt-4 max-w-2xl leading-7 text-muted-foreground">{cv.summary}</p>

        <div className="mt-8 grid gap-6 md:grid-cols-2">
          <div>
            <h2 className="text-sm uppercase tracking-[0.25em] text-muted-foreground">Principles</h2>
            <ul className="mt-4 space-y-3 text-sm leading-6 text-foreground">
              {cv.principles.map((principle) => (
                <li key={principle}>{principle}</li>
              ))}
            </ul>
          </div>

          <div>
            <h2 className="text-sm uppercase tracking-[0.25em] text-muted-foreground">Strengths</h2>
            <ul className="mt-4 space-y-3 text-sm leading-6 text-foreground">
              {cv.strengths.map((strength) => (
                <li key={strength}>{strength}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-8">
          <h2 className="text-sm uppercase tracking-[0.25em] text-muted-foreground">Experience</h2>
          <div className="mt-4 space-y-4">
            {cv.experience.map((item) => (
              <article className="rounded-[1.5rem] border border-border/70 bg-background/60 p-5" key={`${item.company}-${item.role}`}>
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h3 className="text-lg font-semibold">{item.role}</h3>
                    <p className="text-sm text-muted-foreground">{item.company}</p>
                  </div>
                  <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">{item.period}</p>
                </div>
                <p className="mt-4 text-sm leading-6 text-muted-foreground">{item.summary}</p>
                <ul className="mt-4 space-y-2 text-sm leading-6 text-foreground">
                  {item.highlights.map((highlight) => (
                    <li key={highlight}>{highlight}</li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </div>

        <Link className="mt-8 inline-block text-sm text-accent hover:text-primary" href="/">
          &gt; return home
        </Link>
      </section>

      <section className="rounded-[2rem] border border-border/80 bg-card/80 p-6 shadow-terminal sm:p-8">
        <p className="text-xs uppercase tracking-[0.35em] text-primary">portfolio and links</p>
        <h2 className="mt-4 text-2xl font-semibold">{cv.name}</h2>
        <p className="mt-2 text-sm text-muted-foreground">{cv.location}</p>

        <div className="mt-6 flex flex-wrap gap-3">
          {cv.links.map((link) => (
            <a
              className="rounded-full border border-border/80 bg-background/70 px-4 py-2 text-sm transition hover:border-primary/60 hover:text-primary"
              href={link.href}
              key={link.href}
              rel="noreferrer"
              target="_blank"
            >
              {link.label}
            </a>
          ))}
        </div>

        <div className="mt-8">
          <h3 className="text-sm uppercase tracking-[0.25em] text-muted-foreground">Projects</h3>
          <div className="mt-4 space-y-4">
            {projects.map((project) => (
              <article className="rounded-[1.5rem] border border-border/70 bg-background/60 p-5" key={project.name}>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-xs uppercase tracking-[0.25em] text-primary">{project.logo}</p>
                    <h4 className="mt-3 text-lg font-semibold">{project.name}</h4>
                  </div>
                  <span className="rounded-full border border-border/70 px-3 py-1 text-xs uppercase tracking-[0.2em] text-muted-foreground">
                    {project.status}
                  </span>
                </div>
                <p className="mt-4 text-sm leading-6 text-muted-foreground">{project.description}</p>
                <a className="mt-4 inline-block text-sm text-accent hover:text-primary" href={project.url} rel="noreferrer" target="_blank">
                  visit project
                </a>
              </article>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
