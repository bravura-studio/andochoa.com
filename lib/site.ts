import type { Metadata } from "next";

const SITE_URL = "https://andochoa.com";
const SITE_NAME = "ANDOCHOA";
const DEFAULT_DESCRIPTION =
  "Founder notes, systems, and experiments from Andre Ochoa. A monochrome workspace for BUILD.FUN.FREE.";

type BuildPageMetadataOptions = {
  title?: string;
  description?: string;
  path?: string;
};

export const siteConfig = {
  name: SITE_NAME,
  url: SITE_URL,
  description: DEFAULT_DESCRIPTION,
  ogImagePath: "/opengraph-image",
};

export function buildPageMetadata({
  title,
  description = DEFAULT_DESCRIPTION,
  path = "/",
}: BuildPageMetadataOptions = {}): Metadata {
  const fullTitle = title ? `${title} | ${SITE_NAME}` : SITE_NAME;

  return {
    title,
    description,
    alternates: {
      canonical: path,
    },
    openGraph: {
      title: fullTitle,
      description,
      url: path,
      siteName: SITE_NAME,
      images: [siteConfig.ogImagePath],
      locale: "en_US",
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title: fullTitle,
      description,
      images: [siteConfig.ogImagePath],
    },
  };
}
