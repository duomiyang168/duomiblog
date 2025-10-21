export function HeroSection() {
  return (
    <section className="container mx-auto px-4 py-16 md:py-24 text-center">
      <div className="max-w-4xl mx-auto space-y-6">
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
          World&apos;s First{" "}
          <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            Unlimited Free
          </span>
          {" "}AI Image Generator
        </h1>

        <p className="text-xl md:text-2xl text-muted-foreground">
          Powered by FLUX.1-Dev model. No registration required. Superior image quality.
        </p>

        <div className="flex flex-wrap justify-center gap-4 pt-4">
          <div className="flex items-center gap-2 px-4 py-2 bg-secondary rounded-full">
            <span className="text-sm font-medium">✨ Completely Free</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-secondary rounded-full">
            <span className="text-sm font-medium">🚀 No Registration</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-secondary rounded-full">
            <span className="text-sm font-medium">🎨 Unlimited Generation</span>
          </div>
        </div>
      </div>
    </section>
  );
}
