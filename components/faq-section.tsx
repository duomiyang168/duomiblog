import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const faqs = [
  {
    question: "Is Raphael AI really free?",
    answer: "Yes! Raphael AI is completely free with no hidden costs, no subscription fees, and no usage limits. You can generate unlimited images forever.",
  },
  {
    question: "Do I need to create an account?",
    answer: "No registration required! Simply visit our website and start generating images immediately. We believe in making AI accessible to everyone.",
  },
  {
    question: "What AI model powers Raphael AI?",
    answer: "We use the FLUX.1-Dev model, which excels in producing photorealistic images and supports various artistic styles with advanced text understanding capabilities.",
  },
  {
    question: "How long does it take to generate an image?",
    answer: "Image generation typically takes 3-10 seconds depending on complexity and server load. We're constantly optimizing for faster results.",
  },
  {
    question: "Can I use generated images commercially?",
    answer: "Please review the FLUX.1-Dev model's license terms for commercial usage rights. Generally, you retain rights to your creations.",
  },
  {
    question: "What happens to my data?",
    answer: "We implement a strict zero data retention policy. Your prompts and generated images are not stored on our servers, ensuring complete privacy.",
  },
];

export function FAQSection() {
  return (
    <section id="faq" className="container mx-auto px-4 py-16 md:py-24 bg-secondary/30">
      <div className="text-center mb-12">
        <h2 className="text-3xl md:text-4xl font-bold mb-4">
          Frequently Asked Questions
        </h2>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Everything you need to know about Raphael AI
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-5xl mx-auto">
        {faqs.map((faq, index) => (
          <Card key={index}>
            <CardHeader>
              <CardTitle className="text-lg">{faq.question}</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-base">
                {faq.answer}
              </CardDescription>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}
