import Image from 'next/image';

const trustSignals = [
  'Hồ sơ chuyên gia có thông tin xác minh rõ ràng',
  'Yêu cầu tìm nguồn và phản hồi được sắp xếp gọn gàng',
  'Uy tín được xây dựng từ những tương tác thực tế',
];

export default function HomePage() {
  return (
    <main className="home-page">
      <section className="hero">
        <div className="logoWrap">
          <Image
            src="/logo.png"
            alt="NguonTin logo"
            width={220}
            height={220}
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
