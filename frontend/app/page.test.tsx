import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';

import HomePage from './page';

describe('HomePage', () => {
  it('renders the Vietnamese landing page headline with register and login links', () => {
    const html = renderToStaticMarkup(<HomePage />);

    expect(html).toContain('Nơi nhà báo tìm đúng chuyên gia, nhanh hơn và đáng tin hơn');
    expect(html).toContain('Tạo tài khoản');
    expect(html).toContain('href="/register"');
    expect(html).toContain('Đăng nhập bằng email');
    expect(html).toContain('href="/login"');
    expect(html).not.toContain('Tiếp tục với SSO');
    expect(html).toContain('Tìm hiểu cách hoạt động');
  });
});
