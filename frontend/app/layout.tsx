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
      <body>
        <div className="siteShell">
          <div className="siteContent">{children}</div>
          <footer className="siteFooter">
            <div className="siteFooterInner">
              <p className="siteFooterBrand">NguonTin</p>
              <nav aria-label="Liên kết pháp lý" className="siteFooterNav">
                <a href="/privacy">Chính sách quyền riêng tư</a>
                <a href="/terms">Điều khoản sử dụng</a>
              </nav>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
