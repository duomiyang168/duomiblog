import { Navbar } from "@/components/navbar";
import { HeroSection } from "@/components/hero-section";
import { ImageGenerator } from "@/components/image-generator";
import { FeaturesSection } from "@/components/features-section";
import { FAQSection } from "@/components/faq-section";
import { Footer } from "@/components/footer";

export default function Home() {
  return (
    <main className="min-h-screen">
      <Navbar />
      <HeroSection />
      <ImageGenerator />
      <FeaturesSection />
      <FAQSection />
      <Footer />
    </main>
  );
}
