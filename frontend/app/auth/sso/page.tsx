import { Suspense } from 'react';

import SsoCallbackClient from './SsoCallbackClient';

export default function SsoCallbackPage() {
  return (
    <Suspense
      fallback={
        <main className="authPage">
          <section className="authCard">
            <p className="authEyebrow">NguonTin</p>
            <h1>Đang hoàn tất đăng nhập SSO</h1>
            <p className="authDescription">Vui lòng chờ trong giây lát...</p>
          </section>
        </main>
      }
    >
      <SsoCallbackClient />
    </Suspense>
  );
}
