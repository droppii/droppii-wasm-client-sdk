# Ngữ cảnh repository — droppii-wasm-client-sdk

Wrapper TypeScript/WASM của OpenIM cho trình duyệt.

## 1. Trách nhiệm và luồng xử lý

API TypeScript trao đổi với Go WASM; storage dựa vào sql.js/IndexedDB và callback được chuyển lại cho ứng dụng host.

Giữ bộ WASM, wasm_exec và protocol tương thích. Kiểm tra tải asset, nhiều tab, reconnect, migration dữ liệu cục bộ và browser support. Không sửa bundle sinh ra để thay mã nguồn; thay public API phải kiểm tra Chat SDK.

## 2. Điểm bắt đầu trong mã

- [src](../src).
- [assets](../assets).
- [package.json](../package.json).
- [rollup.config.js](../rollup.config.js).

Đọc hướng dẫn tại thư mục con trước khi sửa module tương ứng. Đối chiếu hợp đồng và nơi gọi khi thay đổi API, dữ liệu hoặc thư viện dùng chung.

## 3. Toolchain và kiểm chứng

Phiên bản và lệnh được quản lý trong manifest của từng package; giữ lockfile đang được đường build sử dụng. Với monorepo, chạy tại đúng package hoặc qua workspace. Không nâng toolchain chỉ để làm một lệnh cũ chạy được.

| Manifest | Toolchain được khai báo |
| --- | --- |
| [package.json](../package.json) | node >=12.0; jest ^27.2.0; typescript ^4.2.4 |

| Mục đích | Thư mục chạy | Lệnh | Điều kiện và tác động |
| --- | --- | --- | --- |
| typecheck | `.` | `npm run typecheck` | Kiểm tra tĩnh; không thay thế kiểm thử hành vi. Script: `tsc --noEmit`. |
| lint | `.` | `npm run lint` | Kiểm tra tĩnh; không thay thế kiểm thử hành vi. Có tự sửa file, cần xem diff. Script: `eslint ./src/ --fix`. |
| test | `.` | `npm run test` | Kiểm tra fixture, hook và môi trường trước khi chạy; không mặc định là test cô lập. Script: `jest --coverage`. |
| build | `.` | `npm run build` | Tạo artifact; có thể tải dependency hoặc gọi nguồn dữ liệu khi build, không đồng nghĩa đã deploy. Script: `rimraf lib && rollup -c && tsc-alias`. |

Ghi kết quả và phạm vi thực sự đã chạy trong PR. Không ghi build, lint hoặc test thành công khi mới đọc cấu hình hay khi script không thực thi assertion.

## 4. Cấu hình và phát hành

Đường tự động hóa được xác định trong các workflow sau. Điều kiện branch/tag/path quyết định lúc chạy; bước phát hành cần được đọc cùng quyền và môi trường của job.

| Workflow | Điều kiện kích hoạt |
| --- | --- |
| [.github/workflows/publish.yml](../.github/workflows/publish.yml) | push; branches=main; paths=package.json; workflow_dispatch |

Dùng credential được cấp cho đúng môi trường. Không lưu secret hoặc dữ liệu cá nhân vào mã, tài liệu, ảnh chụp hay log. Migration, seed, publish, gửi thông báo và rollout là thao tác có tác động; chỉ thực hiện trong phạm vi công việc và môi trường đã được giao. Phiên bản đang phục vụ cần được xác định từ artifact/deployment, không chỉ từ default branch.

## 5. Tiêu chuẩn chung và duy trì

Áp dụng [Engineering Standards](https://github.com/droppii/engineering-knowledge/tree/docs/repository-context-pilot/handbook/standards/standards.md), [Principles](https://github.com/droppii/engineering-knowledge/tree/docs/repository-context-pilot/handbook/principles/principles.md) và [AI Context](https://github.com/droppii/engineering-knowledge/tree/docs/repository-context-pilot/handbook/ai-context/README.md). Cấu trúc đang có giải thích cách tìm mã; những phần chưa theo tiêu chuẩn cần được cải thiện khi sửa, không trở thành ngoại lệ mặc định.

Cập nhật tài liệu này trong cùng thay đổi khi module, toolchain, public contract, pipeline hoặc điều kiện kiểm thử thay đổi. Quyết định đặc thù cần được ghi ở repository; kiến thức và tiêu chuẩn dùng chung được duy trì tại Engineering Knowledge.
