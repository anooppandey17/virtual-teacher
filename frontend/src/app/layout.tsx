import type { Metadata } from 'next';
import { Comic_Neue } from 'next/font/google';
import { Toaster } from 'react-hot-toast';
import './globals.css';

// ✅ Import KaTeX CSS globally (for rendering chemical/math formulas)
import 'katex/dist/katex.min.css';

const comic = Comic_Neue({
  weight: ['300', '400', '700'],
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-comic',
});

export const metadata: Metadata = {
  title: 'Virtual Teacher',
  description: 'A platform for virtual teaching and learning',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${comic.variable} font-comic`}>
        <Toaster
          position="top-center"
          toastOptions={{
            duration: 3000,
            style: {
              background: '#4F46E5',
              color: '#fff',
              fontFamily: 'inherit',
            },
          }}
        />
        {children}
      </body>
    </html>
  );
}
