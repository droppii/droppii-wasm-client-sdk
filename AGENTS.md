# Hướng dẫn làm việc — droppii-wasm-client-sdk

## Ngữ cảnh Engineering

Wrapper TypeScript/WASM của OpenIM cho trình duyệt, phát hành lên npm là `@droppii-org/wasm-client-sdk`; consumer trực tiếp là `packages/chat-sdk` trong `droppii/chat`.

Đọc [ngữ cảnh repository](docs/repository-context.md) để chọn đúng module, toolchain, kiểm tra và đường phát hành.

Chuẩn dùng chung: [AI Context](https://github.com/droppii/engineering-knowledge/blob/main/handbook/ai-context/README.md) và [Standards](https://github.com/droppii/engineering-knowledge/blob/main/handbook/standards/standards.md). Ghi revision đã dùng và kết quả kiểm chứng trong PR; cập nhật ngữ cảnh cùng mã.

Giữ bộ WASM, wasm_exec và protocol tương thích. Kiểm tra tải asset, nhiều tab, reconnect, migration dữ liệu cục bộ và browser support. Không sửa bundle sinh ra để thay mã nguồn; thay public API phải kiểm tra Chat SDK.

## Quy tắc bắt buộc

- Dùng npm với [package-lock.json](package-lock.json); Node theo job publish trong [publish.yml](.github/workflows/publish.yml).
- Đồng bộ thay đổi từ Go core (`droppii/openimsdk-core`) bằng skill [droppii-wasm-core-sync](.claude/skills/droppii-wasm-core-sync/SKILL.md); suy ra chữ ký và field từ diff Go thực tế, không đoán theo tên branch. Cập nhật [.core-sync-state.json](.core-sync-state.json) và [SYNC-CHANGELOG.md](SYNC-CHANGELOG.md) trong cùng PR.
- Khi Go core thêm cột DB vào model, thêm cột vào create-table trong [src/sqls](src/sqls) và một hàm `alter*` mới trong [src/api/database/alter.ts](src/api/database/alter.ts); thiếu cột làm các lần ghi qua sql.js lỗi trên trình duyệt đã có dữ liệu.
- Phát hành bằng tăng `version` trong [package.json](package.json) và merge vào `main`; không chạy `npm publish` từ máy local.
- `npm run lint` chạy `eslint --fix` và sửa file; xem diff sau khi chạy.

## Profile thực thi

Đọc [.engineering/README.md](.engineering/README.md) để chọn profile theo module và nhu cầu kiểm chứng. Dùng checkout/worktree do công cụ agent quản lý theo công việc; phân biệt kiểm nguồn, kiểm mã và kiểm thử hành vi.
