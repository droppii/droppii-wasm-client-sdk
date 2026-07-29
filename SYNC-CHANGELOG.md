# Nhật ký đồng bộ Core → JS SDK

## Sync 2026-07-29 — Core dev đến PR#42 (`902c93f1`)

Nguồn audit: `plans/260729-sync-js-wasm-with-core-dev/plan.md` (audit thủ công PR#3–#42 của Core `dev`, baseline PR#2 `32c543ac`). Core `dev` HEAD tại thời điểm audit đó trùng khớp với HEAD lúc chạy sync này — không có PR mới nào phát sinh thêm.

Đã port 5 PR Core sang JS SDK:

| PR Core | Branch | Thay đổi | Bổ sung ở JS SDK |
|---|---|---|---|
| [#23](https://github.com/droppii/openimsdk-core/pull/23) | feat/Func-createMergeMsg | Thêm field `MaxSeq`/`MinSeq` vào `temp_struct.LocalConversation` (wasm/indexdb) | `maxSeq`/`minSeq` trên `ConversationItem` (`src/types/entity.ts`) |
| [#27](https://github.com/droppii/openimsdk-core/pull/27) | feat/new-func-get-conversation-list-app | Export mới `GetConversationListSplitApp` | `getConversationListSplitApp()`, type `SplitConversationAppParams` |
| [#30](https://github.com/droppii/openimsdk-core/pull/30) | feat/Get-list-msg-app | Export mới `GetAdvancedHistoryMessageListApp`, `GetAdvancedHistoryMessageListReverseApp` | `getAdvancedHistoryMessageListApp()`, `getAdvancedHistoryMessageListReverseApp()` |
| [#31](https://github.com/droppii/openimsdk-core/pull/31) | feat/pin-msg | Export mới `PinMsg`, `UnpinMsg`, `GetPinnedMsgs`, `GetPinnedMessageList`; event `OnRecvMessagePinned` | `pinMsg()`, `unpinMsg()`, `getPinnedMsgs()`, `getPinnedMessageList()`, `CbEvents.OnRecvMessagePinned`, type `MessagePinnedInfo`/`PinnedMsgInfo`/`GetPinnedMessageListParams`/`GetPinnedMessageListResult` |
| [#39](https://github.com/droppii/openimsdk-core/pull/39) | feat/new-contentType-Sticker-Message | Content-type mới `StickerMessage = 162`, export `CreateStickerMessage` | `MessageType.StickerMessage = 162`, `createStickerMessage()`, type `StickerElem` |

### Đã loại khỏi phạm vi

- **PR#19** (`createButtonMessage`, feat/DROPPII-29011) — `plan.md` audit trước đó liệt kê là "cần port", nhưng đã xác nhận bằng cách đọc trực tiếp lịch sử Core: PR#19 **đã bị revert** trên `dev` (commit `1cd5f0e2`, nằm trong chính khoảng PR mà `plan.md` từng audit nhưng bị bỏ sót). Không còn `ButtonMessage`/`createButtonMessage` ở bất kỳ file Go nào tại Core `dev` HEAD hiện tại — không port.
- **PR#3/8/9** (field `IsInternal`) — theo `plan.md`: thêm rồi revert 2 lần, net effect không đổi. `isInternal` đã có sẵn ở `MessageItem` từ trước, không cần hành động.
- **PR#5** — chỉ sửa nội bộ schema-guard indexdb, không đổi signature JS.
- **29 PR còn lại** (#6, #10-16, #18, #20-22, #24-26, #28-29, #32-38, #40-42) — không chạm `wasm/`, hoặc là các PR chuẩn bị/follow-up nội bộ cho #27/#30/#31 (đã kiểm tra riêng #29, #32 — không đụng `wasm/`).

### Xác minh riêng — PR#17 (`wasm_exec.js` shim)

`assets/wasm_exec.js` của repo này **có tracked trong git** (không phải build artifact tự động lấy về mỗi lần) — đã kiểm tra trực tiếp: import object đã đổi tên `go` → `gojs` và có harness `_gotest` (khớp PR#17). Tuy nhiên **chưa có** `O_DIRECTORY` và `globalThis.path.resolve` mà PR#17 cũng thêm — file có vẻ đã được cập nhật một phần từ một bản build Core khác, không đồng bộ hoàn toàn với PR#17. Theo yêu cầu, **không chỉnh sửa `assets/`** trong lần sync này (asset sẽ được consumer app override lại) — chỉ ghi nhận để theo dõi.

Version package: `3.8.2-1` → xem commit bump version riêng.
