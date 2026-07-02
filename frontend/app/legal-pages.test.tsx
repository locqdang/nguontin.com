import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';

import PrivacyPolicyPage from './privacy/page';
import TermsOfServicePage from './terms/page';

describe('Legal pages', () => {
  it('renders the Vietnamese privacy policy with contact information', () => {
    const html = renderToStaticMarkup(<PrivacyPolicyPage />);

    expect(html).toContain('Chính sách quyền riêng tư');
    expect(html).toContain('locqdang@gmail.com');
    expect(html).toContain('Thông tin chúng tôi có thể thu thập');
  });

  it('renders the Vietnamese terms page with conduct and contact sections', () => {
    const html = renderToStaticMarkup(<TermsOfServicePage />);

    expect(html).toContain('Điều khoản sử dụng');
    expect(html).toContain('Hành vi bị cấm');
    expect(html).toContain('locqdang@gmail.com');
  });
});
