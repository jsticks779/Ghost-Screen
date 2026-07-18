import { Link } from 'react-router-dom'
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'

const faqs = [
  {
    q: 'What is Ghost Screen?',
    a: 'Ghost Screen is a screen overlay that will help you to secure your desktop if you need a privacy immediately with just one shortcut.',
  },
  {
    q: 'How do I toggle Ghost Screen?',
    a: <>You can toggle Ghost Screen immediately just after install it by shortcut Ctrl+3 but you can change shortcut whenever you want. To change shortcut visit <Link to="/docs" className="text-accent underline underline-offset-2 hover:no-underline">Docs</Link>.</>,
  },
  {
    q: 'How do I install Ghost Screen?',
    a: 'Yes you just need to copy link up there then paste it to your command prompt and then it installs Ghost Screen then boom your set.',
  },
  {
    q: 'Can I customize the appearance?',
    a: 'Yes you can change color, image, video, wallpaper to appear in your Ghost Screen whenever you want.',
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
