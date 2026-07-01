import Image from 'next/image';

const trustSignals = [
  'Hồ sơ chuyên gia có thông tin xác minh rõ ràng',
  'Yêu cầu tìm nguồn và phản hồi được sắp xếp gọn gàng',
  'Uy tín được xây dựng từ những tương tác thực tế',
];

type BackendHealth = {
  ok: boolean;
  status: string;
  detail: string;
  checkedAt: string;
};

async function getBackendHealth(): Promise<BackendHealth> {
  const apiBaseUrl =
    process.env.INTERNAL_API_BASE_URL ??
    process.env.NEXT_PUBLIC_API_BASE_URL ??
    'http://127.0.0.1:8008';

  const checkedAt = new Date().toLocaleString('vi-VN', {
    timeZone: 'Asia/Ho_Chi_Minh',
  });

  try {
    const response = await fetch(`${apiBaseUrl}/health`, {
      cache: 'no-store',
    });

    if (!response.ok) {
      return {
        ok: false,
        status: `HTTP ${response.status}`,
        detail: 'Backend có phản hồi nhưng chưa sẵn sàng.',
        checkedAt,
      };
    }

    const payload = (await response.json()) as {
      status?: string;
      service?: string;
    };

    return {
      ok: true,
      status: payload.status ?? 'healthy',
      detail: `Kết nối thành công tới ${payload.service ?? 'backend API'}.`,
      checkedAt,
    };
  } catch (error) {
    return {
      ok: false,
      status: 'unreachable',
      detail:
        error instanceof Error
          ? `Chưa kết nối được backend: ${error.message}`
          : 'Chưa kết nối được backend.',
      checkedAt,
    };
  }
}

export default async function HomePage() {
  const backendHealth = await getBackendHealth();

  return (
    <main className="home-page">
      <section className="hero">
        <div className="logoWrap">
          <Image
            src="/nguontin-logo.svg"
            alt="NguonTin logo"
            width={220}
            height={72}
            priority
            className="heroLogo"
          />
        </div>
        <p className="eyebrow">NguonTin</p>
        <h1>Nơi nhà báo tìm đúng chuyên gia, nhanh hơn và đáng tin hơn</h1>
        <p className="intro">
          NguonTin giúp nhà báo kết nối với chuyên gia phù hợp thông qua hồ sơ rõ
          ràng, thông tin xác minh minh bạch và quy trình tiếp nhận phản hồi dễ
          theo dõi.
        </p>
        <div className="actions">
          <a
            className="primaryAction"
            href="mailto:nguontin.com@gmail.com?subject=NguonTin%20quan%20tam%20som"
          >
            Nhận thông tin sớm
          </a>
          <a className="secondaryAction" href="#how-it-works">
            Tìm hiểu cách hoạt động
          </a>
        </div>

        <section className="statusPanel" aria-label="Tình trạng kết nối backend">
          <p className="statusEyebrow">Trạng thái API</p>
          <div className="statusSummaryRow">
            <strong
              className={backendHealth.ok ? 'statusBadge statusOk' : 'statusBadge statusError'}
            >
              {backendHealth.ok ? 'Đã kết nối' : 'Chưa kết nối'}
            </strong>
            <span className="statusCode">{backendHealth.status}</span>
          </div>
          <p className="statusDetail">{backendHealth.detail}</p>
          <p className="statusTimestamp">Kiểm tra lúc: {backendHealth.checkedAt}</p>
        </section>
      </section>

      <section className="cardGrid" id="how-it-works">
        <article className="card">
          <h2>Dành cho nhà báo</h2>
          <p>
            Đăng nhu cầu tìm nguồn, nhận phản hồi từ những người phù hợp và quản lý
            toàn bộ quá trình làm việc ở một nơi.
          </p>
        </article>

        <article className="card">
          <h2>Dành cho chuyên gia</h2>
          <p>
            Chia sẻ chuyên môn với đúng người đang cần, xuất hiện chuyên nghiệp hơn
            và từng bước xây dựng uy tín với giới báo chí.
          </p>
        </article>

        <article className="card">
          <h2>Vì sao NguonTin khác hơn</h2>
          <ul>
            {trustSignals.map((signal) => (
              <li key={signal}>{signal}</li>
            ))}
          </ul>
        </article>
      </section>
    </main>
  );
}
