import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Raphael AI - Free Unlimited AI Image Generator",
  description: "World's first unlimited free AI image generator powered by FLUX.1-Dev. No registration required, superior image quality.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
