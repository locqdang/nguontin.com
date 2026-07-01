import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'NguonTin',
  description: 'Nền tảng kết nối chuyên gia đáng tin cậy cho nhà báo nói tiếng Việt.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi">
      <body>{children}</body>
    </html>
  );
}
