'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

const rawApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, '');

function resolveApiBaseUrl() {
  if (rawApiBaseUrl) {
    return rawApiBaseUrl;
  }

  if (typeof window !== 'undefined' && window.location.hostname === 'nguontin.com') {
    return 'https://api.nguontin.com';
  }

  return '';
}

type AuthMode = 'login' | 'register';
type RoleOption = 'journalist' | 'expert';

type StartResponse = {
  message: string;
  email: string;
  auth_flow: AuthMode;
  dev_login_code?: string | null;
};

type AuthSuccess = {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    email: string;
    role: 'journalist' | 'expert' | 'admin';
    full_name: string | null;
    verification_status: string;
    auth_preference: string;
  };
};

const ssoOptions = [
  { value: 'google', label: 'Tiếp tục với Google' },
  { value: 'linkedin', label: 'Tiếp tục với LinkedIn' },
] as const;

const roleLabels: Record<RoleOption, string> = {
  journalist: 'Nhà báo',
  expert: 'Chuyên gia',
};

export default function AuthForm({ mode = 'login' }: { mode?: AuthMode }) {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState<RoleOption>('journalist');
  const [verificationCode, setVerificationCode] = useState('');
  const [pendingCode, setPendingCode] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [isStartingSso, setIsStartingSso] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const apiBaseUrl = resolveApiBaseUrl();
  const isRegister = mode === 'register';

  async function handleStart(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setErrorMessage('');
    setSuccessMessage('');

    if (!apiBaseUrl) {
      setErrorMessage('Hệ thống đăng nhập đang thiếu cấu hình máy chủ. Vui lòng liên hệ quản trị viên.');
      setIsSubmitting(false);
      return;
    }

    try {
      const response = await fetch(`${apiBaseUrl}${isRegister ? '/auth/register' : '/auth/email/start'}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          auth_flow: mode,
          ...(isRegister ? { role, full_name: fullName } : {}),
        }),
      });

      const payload = (await response.json()) as StartResponse & {
        detail?: string;
      };

      if (!response.ok) {
        setErrorMessage(payload.detail || 'Không thể gửi mã đăng nhập lúc này.');
        return;
      }

      setPendingCode(payload.dev_login_code || null);
      setSuccessMessage(
        payload.dev_login_code
          ? `${payload.message} Mã thử nghiệm hiện tại là ${payload.dev_login_code}.`
          : payload.message,
      );
    } catch {
      setErrorMessage('Không thể kết nối tới máy chủ. Vui lòng thử lại sau ít phút.');
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleVerify(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsVerifying(true);
    setErrorMessage('');
    setSuccessMessage('');

    if (!apiBaseUrl) {
      setErrorMessage('Hệ thống đăng nhập đang thiếu cấu hình máy chủ. Vui lòng liên hệ quản trị viên.');
      setIsVerifying(false);
      return;
    }

    try {
      const response = await fetch(`${apiBaseUrl}/auth/email/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          code: verificationCode,
        }),
      });

      const payload = (await response.json()) as Partial<AuthSuccess> & {
        detail?: string;
      };

      if (!response.ok) {
        setErrorMessage(payload.detail || 'Không thể xác nhận mã đăng nhập lúc này.');
        return;
      }

      if (payload.access_token) {
        window.localStorage.setItem('nguontin_access_token', payload.access_token);
      }
      if (payload.user) {
        window.localStorage.setItem('nguontin_current_user', JSON.stringify(payload.user));
      }

      setPendingCode(null);
      setVerificationCode('');
      setSuccessMessage(
        isRegister
          ? 'Tạo tài khoản thành công. Phiên làm việc đã được lưu trên trình duyệt này.'
          : 'Đăng nhập thành công. Phiên làm việc đã được lưu trên trình duyệt này.',
      );

      router.refresh();
    } catch {
      setErrorMessage('Không thể kết nối tới máy chủ. Vui lòng thử lại sau ít phút.');
    } finally {
      setIsVerifying(false);
    }
  }

  async function handleSsoStart(provider: 'google' | 'linkedin') {
    setErrorMessage('');
    setSuccessMessage('');
    setIsStartingSso(provider);

    if (!apiBaseUrl) {
      setErrorMessage('Hệ thống đăng nhập đang thiếu cấu hình máy chủ. Vui lòng liên hệ quản trị viên.');
      setIsStartingSso(null);
      return;
    }

    try {
      const params = new URLSearchParams({ auth_flow: mode });
      if (isRegister) {
        if (!fullName.trim()) {
          setErrorMessage('Vui lòng nhập họ và tên trước khi đăng ký bằng SSO.');
          setIsStartingSso(null);
          return;
        }
        params.set('role', role);
        params.set('full_name', fullName.trim());
      }

      const response = await fetch(`${apiBaseUrl}/auth/sso/${provider}/start?${params.toString()}`);
      const payload = (await response.json()) as {
        authorization_url?: string;
        message?: string;
        detail?: string;
      };

      if (!response.ok || !payload.authorization_url) {
        setErrorMessage(payload.detail || 'Không thể khởi động đăng nhập SSO lúc này.');
        return;
      }

      window.location.assign(payload.authorization_url);
    } catch {
      setErrorMessage('Không thể kết nối tới máy chủ. Vui lòng thử lại sau ít phút.');
    } finally {
      setIsStartingSso(null);
    }
  }

  return (
    <main className="authPage">
      <section className="authCard">
        <a className="authBackLink" href="/">
          ← Về trang chủ
        </a>
        <p className="authEyebrow">NguonTin</p>
        <h1>{isRegister ? 'Tạo tài khoản NguonTin' : 'Đăng nhập vào NguonTin'}</h1>
        <p className="authDescription">
          {isRegister
            ? 'Chọn vai trò, nhập họ tên và email để nhận mã xác thực một lần. Bạn có thể bắt đầu với email hoặc chọn nhà cung cấp SSO phù hợp.'
            : 'Nhập email để nhận mã đăng nhập một lần, hoặc tiếp tục với Google hay LinkedIn.'}
        </p>

        <form className="authForm" onSubmit={handleStart}>
          {isRegister ? (
            <>
              <label className="fieldGroup">
                <span>Vai trò</span>
                <select name="role" onChange={(event) => setRole(event.target.value as RoleOption)} value={role}>
                  {Object.entries(roleLabels).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </label>

              <label className="fieldGroup">
                <span>Họ và tên</span>
                <input
                  autoComplete="name"
                  name="full_name"
                  onChange={(event) => setFullName(event.target.value)}
                  placeholder="Ví dụ: Nguyễn Minh An"
                  required
                  type="text"
                  value={fullName}
                />
              </label>
            </>
          ) : null}

          <label className="fieldGroup">
            <span>Email</span>
            <input
              autoComplete="email"
              name="email"
              onChange={(event) => setEmail(event.target.value)}
              placeholder="ban@example.com"
              required
              type="email"
              value={email}
            />
          </label>

          <button className="primaryAction authSubmit" disabled={isSubmitting} type="submit">
            {isSubmitting
              ? isRegister
                ? 'Đang gửi mã tạo tài khoản...'
                : 'Đang gửi mã...'
              : isRegister
                ? 'Nhận mã để tạo tài khoản'
                : 'Nhận mã đăng nhập'}
          </button>
        </form>

        <form className="authForm authVerifyForm" onSubmit={handleVerify}>
          <label className="fieldGroup">
            <span>Mã đăng nhập một lần</span>
            <input
              inputMode="numeric"
              name="verification_code"
              onChange={(event) => setVerificationCode(event.target.value)}
              placeholder="Nhập mã gồm 6 chữ số"
              required
              type="text"
              value={verificationCode}
            />
          </label>

          {pendingCode ? (
            <p className="authHint">
              Mã thử nghiệm hiện tại: <strong>{pendingCode}</strong>
            </p>
          ) : null}

          {errorMessage ? <p className="formMessage formMessageError">{errorMessage}</p> : null}
          {successMessage ? <p className="formMessage formMessageSuccess">{successMessage}</p> : null}

          <button className="secondaryAction authSubmit" disabled={isVerifying} type="submit">
            {isVerifying
              ? 'Đang xác nhận...'
              : isRegister
                ? 'Xác nhận mã và tạo tài khoản'
                : 'Xác nhận mã và đăng nhập'}
          </button>
        </form>

        <div className="authSsoSection">
          <p className="authSsoHeading">Hoặc tiếp tục với nhà cung cấp SSO</p>
          <div className="authSsoActions">
            {ssoOptions.map((option) => {
              const isThisProviderLoading = isStartingSso === option.value;
              return (
                <button
                  key={option.value}
                  className="secondaryAction authSsoButton"
                  disabled={Boolean(isStartingSso)}
                  onClick={() => handleSsoStart(option.value)}
                  type="button"
                >
                  {isThisProviderLoading ? 'Đang chuyển hướng...' : option.label}
                </button>
              );
            })}
          </div>
        </div>

        <p className="authAlternate">
          {isRegister ? 'Đã có tài khoản?' : 'Chưa có tài khoản?'}{' '}
          <a href={isRegister ? '/login' : '/register'}>
            {isRegister ? 'Đăng nhập tại đây' : 'Tạo tài khoản ngay'}
          </a>
        </p>
      </section>
    </main>
  );
}
