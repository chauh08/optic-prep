import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "OpticPrep — Opticianry practice",
  description: "Independent practice for ABO Basic Certification candidates."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  const concept = "<!-- THESIS: Precision before pace. OWN-WORLD: A quiet optical workbench of ink, ivory, cyan, and measurement marks. STORY: Configure, focus, verify, review. FIRST VIEWPORT: The next study decision and evidence of readiness. FORM: Instrument-like controls, square edges, clear axes, no decorative gamification. -->";
  return (
    <html lang="en">
      <body>
        <span aria-hidden="true" className="markup-note" dangerouslySetInnerHTML={{ __html: concept }} />
        {children}
      </body>
    </html>
  );
}
