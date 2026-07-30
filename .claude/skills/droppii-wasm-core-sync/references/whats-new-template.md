# Format File Tổng Hợp "What's New"

File: `SYNC-CHANGELOG.md` ở root JS repo (thêm 1 section mới theo ngày mỗi lần chạy — không ghi đè các entry trước).

## Template

```markdown
## Sync YYYY-MM-DD — Core dev đến PR#<pr-cao-nhất> (`<sha>`)

Đã sync <N> PR Core sang JS SDK:

| PR Core | Branch | Thay đổi | Bổ sung ở JS SDK |
|---|---|---|---|
| #19 | feat/DROPPII-29011(button-contentType) | Export mới `createButtonMessage` | `MessageType.ButtonMessage`, `createButtonMessage()`, `ButtonElem` |
| #27 | feat/new-func-get-conversation-list-app | Export mới `getConversationListSplitApp` | Method `getConversationListSplitApp()` |
| #39 | feat/new-contentType-Sticker-Message | Export mới `createStickerMessage` | `MessageType.StickerMessage = 162`, `createStickerMessage()`, `StickerElem` |

Bỏ qua (không cần hành động): #10, #11, #12 (chỉ nội bộ Core — xem bảng audit đầy đủ nếu còn giữ).

Version package: `3.8.2-1` → `3.9.0`.
```

## Quy tắc

- Mỗi PR đã port 1 dòng — link PR tới `https://github.com/droppii/openimsdk-core/pull/<n>` nếu định dạng hỗ trợ.
- PR bị bỏ qua liệt kê gộp trong cùng section (list PR#, phẩy cách nhau), không cần 1 dòng riêng như PR đã port.
- Nếu có sẵn 1 file plan/audit của lần trước (ví dụ `plans/*/plan.md`) và đã dùng làm baseline cho lần chạy này, chỉ ghi 1 dòng "Nguồn audit" trỏ tới file đó, không lặp lại nội dung.
- Toàn bộ nội dung `SYNC-CHANGELOG.md` viết bằng **tiếng Việt** (theo yêu cầu team) — kể cả tiêu đề section, mô tả thay đổi. Tên hàm/type/PR branch giữ nguyên tiếng Anh (đây là code, không dịch).
