import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'

const faqs = [
  {
    q: 'What is Ghost Screen?',
    a: 'Ghost Screen is a full-screen animated ghost overlay that functions as a screensaver. It covers all monitors with a cyberpunk holographic animation and blocks input until toggled off.',
  },
  {
    q: 'How do I toggle Ghost Screen?',
    a: 'Press Ctrl+3 to toggle the ghost on and off. You can customize this shortcut in the config file.',
  },
  {
    q: 'Does it work on Windows?',
    a: 'Yes! Ghost Screen works on Windows using only Python\'s built-in tkinter and ctypes — no external dependencies needed.',
  },
  {
    q: 'Can I customize the appearance?',
    a: 'Yes, you can change colors, opacity, animation speed, and particle count via a JSON config file.',
  },
  {
    q: 'Is it free and open source?',
    a: 'Yes, Ghost Screen is completely free and open source under the MIT license.',
  },
]

export default function FAQ() {
  return (
    <section className="py-24 px-6" id="faq">
      <div className="max-w-2xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12">FAQ</h2>
        <Accordion className="w-full">
          {faqs.map((faq, i) => (
            <AccordionItem key={i}>
              <AccordionTrigger className="text-left text-sm font-medium">
                {faq.q}
              </AccordionTrigger>
              <AccordionContent className="text-sm text-muted-foreground leading-relaxed">
                {faq.a}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </section>
  )
}
