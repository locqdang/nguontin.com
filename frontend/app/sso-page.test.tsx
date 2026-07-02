import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';

import SsoCallbackPage from './auth/sso/page';

describe('SSO callback page', () => {
  it('renders the Vietnamese SSO fallback shell', () => {
    const html = renderToStaticMarkup(<SsoCallbackPage />);

    expect(html).toContain('Đang hoàn tất đăng nhập SSO');
    expect(html).toContain('Vui lòng chờ trong giây lát...');
  });
});
