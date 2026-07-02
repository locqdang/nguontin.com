import { renderToStaticMarkup } from 'react-dom/server';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import LoginPage from './login/page';
import RegisterPage from './register/page';

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    refresh: vi.fn(),
  }),
}));

describe('Auth pages', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the Vietnamese login screen with email and SSO actions', () => {
    const html = renderToStaticMarkup(<LoginPage />);

    expect(html).toContain('Đăng nhập vào NguonTin');
    expect(html).toContain('Nhập email để nhận mã đăng nhập một lần');
    expect(html).toContain('Tiếp tục với Google');
    expect(html).toContain('Tiếp tục với LinkedIn');
    expect(html).toContain('href="/register"');
  });

  it('renders the Vietnamese registration screen with role and full-name fields', () => {
    const html = renderToStaticMarkup(<RegisterPage />);

    expect(html).toContain('Tạo tài khoản NguonTin');
    expect(html).toContain('Vai trò');
    expect(html).toContain('Họ và tên');
    expect(html).toContain('Nhận mã để tạo tài khoản');
    expect(html).toContain('href="/login"');
  });
});
