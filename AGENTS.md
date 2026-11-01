# Hướng dẫn làm việc — droppii-wasm-client-sdk

## Ngữ cảnh Engineering

Wrapper TypeScript/WASM của OpenIM cho trình duyệt.

Đọc [ngữ cảnh repository](docs/repository-context.md) để chọn đúng module, toolchain, kiểm tra và đường phát hành. Đọc hướng dẫn thư mục con khi đi vào phạm vi tương ứng.

Chuẩn dùng chung: [AI Context](https://github.com/droppii/engineering-knowledge/tree/docs/repository-context-pilot/handbook/ai-context/README.md) và [Standards](https://github.com/droppii/engineering-knowledge/tree/docs/repository-context-pilot/handbook/standards/standards.md). Ghi revision đã dùng và kết quả kiểm chứng trong PR; cập nhật ngữ cảnh cùng mã.

Giữ bộ WASM, wasm_exec và protocol tương thích. Kiểm tra tải asset, nhiều tab, reconnect, migration dữ liệu cục bộ và browser support. Không sửa bundle sinh ra để thay mã nguồn; thay public API phải kiểm tra Chat SDK.

## Profile thực thi

Đọc [.engineering/README.md](.engineering/README.md) để chọn profile theo module và nhu cầu kiểm chứng. Dùng checkout/worktree do công cụ agent quản lý theo công việc; phân biệt kiểm nguồn, kiểm mã và kiểm thử hành vi.
