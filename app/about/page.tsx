import { AboutShell } from "@/components/about-shell";
import { buildPageMetadata } from "@/lib/site";

export const metadata = buildPageMetadata({
  title: "About",
  description: "Background, experience, and founder profile for Andre Ochoa.",
  path: "/about",
});

export default function AboutPage() {
  return <AboutShell />;
}
