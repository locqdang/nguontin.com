import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Chính sách quyền riêng tư | NguonTin',
  description:
    'Chính sách quyền riêng tư của NguonTin dành cho nhà báo, chuyên gia và người dùng truy cập nền tảng.',
};

const privacySections = [
  {
    title: '1. Phạm vi áp dụng',
    paragraphs: [
      'Chính sách này áp dụng cho website, các trang đăng ký và đăng nhập, hồ sơ người dùng, biểu mẫu xác minh và các tương tác liên quan đến nền tảng NguonTin.',
      'Khi bạn truy cập hoặc sử dụng NguonTin, bạn đồng ý để chúng tôi thu thập và xử lý thông tin theo phạm vi được mô tả dưới đây.',
    ],
  },
  {
    title: '2. Thông tin chúng tôi có thể thu thập',
    paragraphs: [
      'Chúng tôi có thể thu thập thông tin bạn chủ động cung cấp, bao gồm họ tên, địa chỉ email, vai trò sử dụng (nhà báo, chuyên gia hoặc quản trị viên), thông tin hồ sơ nghề nghiệp và nội dung bạn gửi qua các biểu mẫu trên nền tảng.',
      'Nếu bạn dùng đăng nhập bằng email hoặc SSO, chúng tôi có thể xử lý dữ liệu cần thiết để xác minh danh tính, tạo phiên đăng nhập và bảo vệ tài khoản của bạn.',
      'Trong quá trình xác minh hồ sơ, chúng tôi có thể lưu thông tin, tài liệu hoặc liên kết do bạn gửi để chứng minh chuyên môn, đơn vị công tác hoặc mức độ phù hợp với vai trò trên nền tảng.',
    ],
  },
  {
    title: '3. Cách chúng tôi sử dụng dữ liệu',
    paragraphs: [
      'NguonTin sử dụng dữ liệu để tạo và quản lý tài khoản, xác minh danh tính hoặc thông tin nghề nghiệp, hiển thị hồ sơ, hỗ trợ kết nối giữa nhà báo và chuyên gia, và duy trì an toàn cho nền tảng.',
      'Chúng tôi cũng có thể dùng dữ liệu để gửi email liên quan đến đăng nhập, xác minh tài khoản, thông báo vận hành quan trọng, cập nhật hồ sơ hoặc phản hồi đối với yêu cầu hỗ trợ.',
      'Chúng tôi không dùng dữ liệu cá nhân của bạn cho mục đích bán dữ liệu cho bên thứ ba.',
    ],
  },
  {
    title: '4. Dữ liệu đăng nhập và bảo mật tài khoản',
    paragraphs: [
      'Dữ liệu đăng nhập, như mã xác thực một lần, thông tin trạng thái đăng nhập hoặc dữ liệu cần thiết cho phiên SSO, chỉ được xử lý trong phạm vi cần thiết để xác thực và bảo vệ tài khoản.',
      'Chúng tôi có thể lưu các bản ghi kỹ thuật giới hạn để phát hiện lạm dụng, khắc phục lỗi và tăng độ an toàn cho hệ thống, nhưng sẽ tránh lưu trữ dữ liệu nhạy cảm nhiều hơn mức cần thiết.',
    ],
  },
  {
    title: '5. Xác minh hồ sơ và bằng chứng xác minh',
    paragraphs: [
      'Nếu nền tảng yêu cầu xác minh vai trò hoặc chuyên môn, NguonTin có thể xem xét thông tin hồ sơ, liên kết công khai, tài liệu xác minh hoặc nội dung bạn gửi để đánh giá độ tin cậy.',
      'Thông tin xác minh được dùng để hỗ trợ quyết định vận hành và tăng độ tin cậy của hồ sơ. Chúng tôi không cam kết công khai toàn bộ tài liệu xác minh, và có thể chỉ hiển thị trạng thái hoặc tín hiệu xác minh phù hợp cho người dùng khác.',
    ],
  },
  {
    title: '6. Chia sẻ dữ liệu',
    paragraphs: [
      'Chúng tôi có thể chia sẻ một phần dữ liệu hồ sơ hoặc tín hiệu xác minh với người dùng khác trên nền tảng khi điều đó cần thiết để hỗ trợ kết nối giữa nhà báo và chuyên gia.',
      'Chúng tôi cũng có thể sử dụng nhà cung cấp hạ tầng, dịch vụ email hoặc dịch vụ xác thực để vận hành NguonTin. Các bên này chỉ được truy cập dữ liệu trong phạm vi cần thiết để cung cấp dịch vụ cho chúng tôi.',
      'Chúng tôi có thể tiết lộ dữ liệu khi pháp luật yêu cầu hoặc khi cần thiết để bảo vệ quyền lợi, an toàn hoặc tính toàn vẹn của NguonTin và cộng đồng người dùng.',
    ],
  },
  {
    title: '7. Lưu giữ dữ liệu',
    paragraphs: [
      'Chúng tôi lưu dữ liệu trong khoảng thời gian hợp lý để vận hành tài khoản, hỗ trợ xác minh, tuân thủ nghĩa vụ pháp lý, giải quyết tranh chấp hoặc bảo vệ nền tảng trước hành vi lạm dụng.',
      'Khi dữ liệu không còn cần thiết cho các mục đích đó, chúng tôi sẽ xem xét xóa hoặc ẩn danh dữ liệu theo khả năng vận hành của hệ thống.',
    ],
  },
  {
    title: '8. Quyền và lựa chọn của bạn',
    paragraphs: [
      'Bạn có thể yêu cầu cập nhật thông tin hồ sơ, chỉnh sửa dữ liệu không chính xác, hoặc liên hệ với chúng tôi về việc xem xét xóa tài khoản hoặc dữ liệu liên quan, tùy theo nghĩa vụ lưu giữ và yêu cầu vận hành hợp lý.',
      'Nếu bạn cho rằng dữ liệu của mình đang được xử lý không phù hợp, bạn có thể liên hệ với chúng tôi để được xem xét.',
    ],
  },
  {
    title: '9. Liên hệ',
    paragraphs: [
      'Nếu bạn có câu hỏi về quyền riêng tư, dữ liệu tài khoản hoặc việc xác minh hồ sơ, vui lòng liên hệ NguonTin qua email: locqdang@gmail.com.',
    ],
  },
  {
    title: '10. Cập nhật chính sách',
    paragraphs: [
      'Chúng tôi có thể cập nhật chính sách này khi phạm vi sản phẩm, quy trình xác minh hoặc cách vận hành thay đổi. Phiên bản cập nhật sẽ được đăng trên trang này.',
    ],
  },
] as const;

export default function PrivacyPolicyPage() {
  return (
    <main className="legalPage">
      <section className="legalShell">
        <p className="legalEyebrow">NguonTin</p>
        <h1>Chính sách quyền riêng tư</h1>
        <p className="legalLead">
          NguonTin tôn trọng quyền riêng tư của nhà báo, chuyên gia và mọi người dùng
          truy cập nền tảng. Trang này giải thích chúng tôi có thể thu thập dữ liệu gì,
          vì sao dữ liệu đó được dùng và cách bạn có thể liên hệ với chúng tôi về các
          vấn đề liên quan đến tài khoản hoặc quyền riêng tư.
        </p>

        <div className="legalMeta">
          <p>
            <strong>Ngày hiệu lực:</strong> 02/07/2026
          </p>
          <p>
            <strong>Liên hệ:</strong> <a href="mailto:locqdang@gmail.com">locqdang@gmail.com</a>
          </p>
        </div>

        <div className="legalContent">
          {privacySections.map((section) => (
            <section key={section.title} className="legalSection">
              <h2>{section.title}</h2>
              {section.paragraphs.map((paragraph) => (
                <p key={paragraph}>{paragraph}</p>
              ))}
            </section>
          ))}
        </div>
      </section>
    </main>
  );
}
