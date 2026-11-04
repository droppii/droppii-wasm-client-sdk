# Ngữ cảnh repository — droppii-wasm-client-sdk

Wrapper TypeScript/WASM của OpenIM cho trình duyệt.

## 1. Trách nhiệm và luồng xử lý

API TypeScript trao đổi với Go WASM; storage dựa vào sql.js/IndexedDB và callback được chuyển lại cho ứng dụng host. Repo được fork từ OpenIM SDK web; logic nghiệp vụ và mô hình dữ liệu cục bộ đi theo `droppii/openimsdk-core` (branch `dev`), không theo upstream OpenIM.

Package không chứa `openIM.wasm`. Binary này được build ở Go core và host tự phục vụ theo URL truyền vào `getSDK({ coreWasmPath })`; package chỉ mang `sql-wasm.wasm` và `wasm_exec.js` trong [assets](../assets). Vì vậy binary chạy trên môi trường và bản JS consumer đang dùng có thể lệch nhau: khi core thêm cột DB, mọi web consumer phải lên bản JS có cột đó trước khi binary mới được triển khai cho môi trường tương ứng.

Giữ bộ WASM, wasm_exec và protocol tương thích. Kiểm tra tải asset, nhiều tab, reconnect, migration dữ liệu cục bộ và browser support. Không sửa bundle sinh ra để thay mã nguồn; thay public API phải kiểm tra Chat SDK.

## 2. Điểm bắt đầu trong mã

| Loại thay đổi | Đường dẫn | Phụ thuộc cần xét |
| --- | --- | --- |
| Public API, `getSDK` và method gọi Go | [src/sdk/index.ts](../src/sdk/index.ts), [src/index.ts](../src/index.ts) | Chữ ký export của Go core; consumer `packages/chat-sdk` |
| Kiểu dữ liệu, enum, sự kiện | [src/types](../src/types), [src/constant](../src/constant) | Struct và hằng số của Go core |
| Bảng SQL cục bộ và migration | [src/sqls](../src/sqls), [src/api/database](../src/api/database) | `model_struct` của Go core; dữ liệu IndexedDB đã có trên trình duyệt |
| Worker và kết nối DB | [src/api/worker.ts](../src/api/worker.ts), [src/api/index.ts](../src/api/index.ts) | Bundle `lib/worker.js` trong [rollup.config.js](../rollup.config.js) |
| Đồng bộ với Go core | [.claude/skills/droppii-wasm-core-sync](../.claude/skills/droppii-wasm-core-sync/SKILL.md), [.core-sync-state.json](../.core-sync-state.json), [SYNC-CHANGELOG.md](../SYNC-CHANGELOG.md) | Lịch sử PR core đã port hoặc bỏ qua |

## 3. Toolchain và kiểm chứng

Toolchain: npm với [package-lock.json](../package-lock.json); repo không có `.nvmrc`, `engines` trong [package.json](../package.json) khai báo rất rộng, job publish dùng Node khai báo trong [publish.yml](../.github/workflows/publish.yml). TypeScript, ESLint và Rollup theo devDependencies của manifest. Không nâng toolchain chỉ để làm một lệnh cũ chạy được.

| Mục đích | Thư mục chạy | Lệnh | Điều kiện và tác động |
| --- | --- | --- | --- |
| typecheck | `.` | `npm run typecheck` | Kiểm tra tĩnh; không thay thế kiểm thử hành vi. |
| lint | `.` | `npm run lint` | Chạy với `--fix`, sửa file; cần xem diff. |
| build | `.` | `npm run build` | Xóa và tạo lại `lib` bằng Rollup; không đồng nghĩa đã publish. |
| test skill đồng bộ | `.` | `python3 -m unittest discover -s .claude/skills/droppii-wasm-core-sync/scripts/tests` | Chỉ kiểm script audit PR core, dùng repo git tạm, không gọi mạng. |

Repo chưa có test JavaScript: `npm run test` gọi Jest nhưng không có file test nào để chạy. Thay đổi SQL hoặc tham số gọi Go cần tái hiện bằng sql.js/squel hoặc kiểm trên consumer, rồi ghi cách kiểm vào PR và SYNC-CHANGELOG.

Ghi kết quả và phạm vi thực sự đã chạy trong PR. Không ghi build, lint hoặc test thành công khi mới đọc cấu hình hay khi script không thực thi assertion.

## 4. Cấu hình và phát hành

[publish.yml](../.github/workflows/publish.yml) chạy khi push lên `main` có đổi `package.json` (hoặc chạy tay): publish lên npm nếu version khác bản đã phát hành, chờ registry phục vụ bản mới, rồi mở PR tại `droppii/chat` để nâng dependency của `packages/chat-sdk`. PR đó chưa tự chạy type-check/build phía chat; người review phải chạy.

Hook husky chạy `lint-staged` trước commit và commitizen khi soạn commit message.

Dùng credential được cấp cho đúng môi trường. Không lưu secret hoặc dữ liệu cá nhân vào mã, tài liệu, ảnh chụp hay log. Publish và cập nhật binary `openIM.wasm` là thao tác có tác động; chỉ thực hiện trong phạm vi công việc và môi trường đã được giao. Phiên bản đang phục vụ cần được xác định từ bản npm và binary đang được host, không chỉ từ default branch.

## 5. Tiêu chuẩn chung và duy trì

Áp dụng [Engineering Standards](https://github.com/droppii/engineering-knowledge/blob/main/handbook/standards/standards.md), [Principles](https://github.com/droppii/engineering-knowledge/blob/main/handbook/principles/principles.md) và [AI Context](https://github.com/droppii/engineering-knowledge/blob/main/handbook/ai-context/README.md). Cấu trúc đang có giải thích cách tìm mã; những phần chưa theo tiêu chuẩn cần được cải thiện khi sửa, không trở thành ngoại lệ mặc định.

Cập nhật tài liệu này trong cùng thay đổi khi module, toolchain, public contract, pipeline hoặc điều kiện kiểm thử thay đổi. Quyết định đặc thù cần được ghi ở repository; kiến thức và tiêu chuẩn dùng chung được duy trì tại Engineering Knowledge.

## Profile và workspace theo công việc

[Profile thực thi của repository](../.engineering/README.md) cung cấp cấu hình theo module và điểm vào kiểm chứng local. Chọn profile trong workspace của công việc, chuẩn bị đúng toolchain/dependency, rồi ghi kết quả và giới hạn vào hồ sơ. Kiểm cấu hình hoặc cú pháp thành công chưa thay thế unit/integration test.
