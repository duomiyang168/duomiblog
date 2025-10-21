import { Sparkles, Zap, Shield, Palette, Clock, Star } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const features = [
  {
    icon: Sparkles,
    title: "Completely Free",
    description: "No hidden fees, no credit card required, no usage limits. Generate unlimited images forever.",
  },
  {
    icon: Zap,
    title: "No Registration",
    description: "Start creating immediately. No account creation, no email verification, no waiting.",
  },
  {
    icon: Palette,
    title: "Multiple Art Styles",
    description: "From photorealistic to anime, oil painting to digital art. Express your creativity freely.",
  },
  {
    icon: Shield,
    title: "Privacy Protected",
    description: "Zero data retention policy. Your prompts and images are never stored on our servers.",
  },
  {
    icon: Clock,
    title: "Fast Generation",
    description: "Powered by FLUX.1-Dev model for quick, high-quality image generation in seconds.",
  },
  {
    icon: Star,
    title: "Superior Quality",
    description: "Advanced text understanding and photorealistic output with excellent detail preservation.",
  },
];

export function FeaturesSection() {
  return (
    <section id="features" className="container mx-auto px-4 py-16 md:py-24">
      <div className="text-center mb-12">
        <h2 className="text-3xl md:text-4xl font-bold mb-4">
          Why Choose Raphael AI?
        </h2>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          The most powerful, free, and accessible AI image generator on the web
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
        {features.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <Card key={index} className="border-2 hover:border-primary/50 transition-colors">
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <Icon className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>{feature.title}</CardTitle>
                <CardDescription className="text-base">
                  {feature.description}
                </CardDescription>
              </CardHeader>
            </Card>
          );
        })}
      </div>
    </section>
  );
}
