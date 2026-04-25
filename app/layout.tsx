import type { Metadata } from "next";
import { Geist_Mono } from "next/font/google";
import { SiteShell } from "@/components/site-shell";
import { buildPageMetadata, siteConfig } from "@/lib/site";
import "./globals.css";

const geistMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-geist-mono",
});

export const metadata: Metadata = {
  metadataBase: new URL(siteConfig.url),
  applicationName: siteConfig.name,
  title: {
    default: siteConfig.name,
    template: `%s | ${siteConfig.name}`,
  },
  keywords: ["Andre Ochoa", "BUILD.FUN.FREE", "founder notes", "writing", "systems", "portfolio"],
  authors: [{ name: "Andre Ochoa" }],
  creator: "Andre Ochoa",
  publisher: "Andre Ochoa",
  category: "technology",
  ...buildPageMetadata(),
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html className="dark" lang="en">
      <body className={`${geistMono.variable} antialiased`}>
        <SiteShell>{children}</SiteShell>
      </body>
    </html>
  );
}
