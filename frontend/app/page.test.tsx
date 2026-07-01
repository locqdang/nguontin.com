import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';

import HomePage from './page';

describe('HomePage', () => {
  it('renders the Vietnamese landing page headline and CTA links', () => {
    const html = renderToStaticMarkup(<HomePage />);

    expect(html).toContain('Nơi nhà báo tìm đúng chuyên gia, nhanh hơn và đáng tin hơn');
    expect(html).toContain('Nhận thông tin sớm');
    expect(html).toContain('mailto:nguontin.com@gmail.com?subject=NguonTin%20quan%20tam%20som');
    expect(html).toContain('Tìm hiểu cách hoạt động');
  });
});
