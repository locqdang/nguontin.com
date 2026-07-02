'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

type SsoUser = {
  id: number;
  email: string;
  role: 'journalist' | 'expert' | 'admin';
  full_name: string | null;
  verification_status: string;
  auth_preference: string;
};

export default function SsoCallbackClient() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const success = searchParams.get('success') === '1';
  const accessToken = searchParams.get('access_token');
  const rawUser = searchParams.get('user');
  const statusMessage = searchParams.get('message') || 'Đang hoàn tất đăng nhập SSO...';
  const [message, setMessage] = useState(statusMessage);

  const parsedUser = useMemo(() => {
    if (!rawUser) {
      return null;
    }

    try {
      return JSON.parse(rawUser) as SsoUser;
    } catch {
      return null;
    }
  }, [rawUser]);

  useEffect(() => {
    setMessage(statusMessage);

    if (success && accessToken) {
      window.localStorage.setItem('nguontin_access_token', accessToken);
    }
    if (success && parsedUser) {
      window.localStorage.setItem('nguontin_current_user', JSON.stringify(parsedUser));
    }

    const timeout = window.setTimeout(() => {
      router.replace(success ? '/' : '/login');
      router.refresh();
    }, 1200);

    return () => window.clearTimeout(timeout);
  }, [accessToken, parsedUser, router, statusMessage, success]);

  return (
    <main className="authPage">
      <section className="authCard">
        <p className="authEyebrow">NguonTin</p>
        <h1>{success ? 'Đăng nhập SSO thành công' : 'Không thể đăng nhập bằng SSO'}</h1>
        <p className="authDescription">{message}</p>
        <p className="authAlternate">
          {success ? 'Đang chuyển bạn về trang chính...' : 'Bạn sẽ được chuyển về trang đăng nhập sau giây lát...'}
        </p>
      </section>
    </main>
  );
}
